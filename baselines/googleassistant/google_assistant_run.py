from pathlib import Path
import unicodedata, re, subprocess
from tqdm import tqdm
import numpy as np
import random
import time
import pandas as pd

cur_file = Path(__file__).parent.absolute()


# Adapted from https://github.com/googlesamples/assistant-sdk-python/blob/ce76c508fdf076678/
#   google-assistant-sdk/googlesamples/assistant/grpc/textinput.py
# Copyright (C) 2017 Google Inc. Avail under apache 2.0 license

import os
import logging
import json

import click
import google.auth.transport.grpc
import google.auth.transport.requests
import google.oauth2.credentials

from google.assistant.embedded.v1alpha2 import (
    embedded_assistant_pb2,
    embedded_assistant_pb2_grpc
)

try:
    from . import (
        assistant_helpers,
        browser_helpers,
    )
except (SystemError, ImportError):
    import assistant_helpers
    import browser_helpers


ASSISTANT_API_ENDPOINT = 'embeddedassistant.googleapis.com'
DEFAULT_GRPC_DEADLINE = 60 * 3 + 5
PLAYING = embedded_assistant_pb2.ScreenOutConfig.PLAYING


def slugify(value, allow_unicode=False):
    # https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


class SampleTextAssistant(object):
    """Sample Assistant that supports text based conversations.

    Args:
      language_code: language for the conversation.
      device_model_id: identifier of the device model.
      device_id: identifier of the registered device instance.
      display: enable visual display of assistant response.
      channel: authorized gRPC channel for connection to the
        Google Assistant API.
      deadline_sec: gRPC deadline in seconds for Google Assistant API call.
    """

    def __init__(self, language_code, device_model_id, device_id,
                 display, channel, deadline_sec):
        self.language_code = language_code
        self.device_model_id = device_model_id
        self.device_id = device_id
        self.conversation_state = None
        # Force reset of first conversation.
        self.is_new_conversation = True
        self.display = display
        self.assistant = embedded_assistant_pb2_grpc.EmbeddedAssistantStub(
            channel
        )
        self.deadline = deadline_sec

    def __enter__(self):
        return self

    def __exit__(self, etype, e, traceback):
        if e:
            return False

    def assist(self, text_query):
        """Send a text request to the Assistant and playback the response.
        """
        def iter_assist_requests():
            config = embedded_assistant_pb2.AssistConfig(
                audio_out_config=embedded_assistant_pb2.AudioOutConfig(
                    encoding='LINEAR16',
                    sample_rate_hertz=16000,
                    volume_percentage=0,
                ),
                dialog_state_in=embedded_assistant_pb2.DialogStateIn(
                    language_code=self.language_code,
                    conversation_state=self.conversation_state,
                    is_new_conversation=self.is_new_conversation,
                ),
                device_config=embedded_assistant_pb2.DeviceConfig(
                    device_id=self.device_id,
                    device_model_id=self.device_model_id,
                ),
                text_query=text_query,
            )
            # Continue current conversation with later requests.
            #self.is_new_conversation = False
            self.is_new_conversation = True

            if self.display:
                config.screen_out_config.screen_mode = PLAYING
            req = embedded_assistant_pb2.AssistRequest(config=config)
            assistant_helpers.log_assist_request_without_audio(req)
            yield req

        text_response = None
        html_response = None
        all_resp_objs = []
        audio_bytes = []
        for resp in self.assistant.Assist(iter_assist_requests(),
                                          self.deadline):
            assistant_helpers.log_assist_response_without_audio(resp)
            if resp.screen_out.data:
                html_response = resp.screen_out.data
            if resp.dialog_state_out.conversation_state:
                conversation_state = resp.dialog_state_out.conversation_state
                self.conversation_state = conversation_state
            if resp.dialog_state_out.supplemental_display_text:
                text_response = resp.dialog_state_out.supplemental_display_text
            if resp.audio_out.audio_data:
                audio_bytes.append(resp.audio_out.audio_data)
            all_resp_objs.append(resp)
        return text_response, html_response, resp, all_resp_objs, b"".join(audio_bytes)


#@click.command()
#@click.option('--api-endpoint', default=ASSISTANT_API_ENDPOINT,
#              metavar='<api endpoint>', show_default=True,
#              help='Address of Google Assistant API service.')
#@click.option('--credentials',
#              metavar='<credentials>', show_default=True,
#              default=os.path.join(click.get_app_dir('google-oauthlib-tool'),
#                                   'credentials.json'),
#              help='Path to read OAuth2 credentials.')
#@click.option('--device-model-id',
#              metavar='<device model id>',
#              required=True,
#              help=(('Unique device model identifier, '
#                     'if not specifed, it is read from --device-config')))
#@click.option('--device-id',
#              metavar='<device id>',
#              required=True,
#              help=(('Unique registered device instance identifier, '
#                     'if not specified, it is read from --device-config, '
#                     'if no device_config found: a new device is registered '
#                     'using a unique id and a new device config is saved')))
#@click.option('--lang', show_default=True,
#              metavar='<language code>',
#              default='en-US',
#              help='Language code of the Assistant')
#@click.option('--display', is_flag=True, default=False,
#              help='Enable visual display of Assistant responses in HTML.')
#@click.option('--verbose', '-v', is_flag=True, default=False,
#              help='Verbose logging.')
#@click.option('--grpc-deadline', default=DEFAULT_GRPC_DEADLINE,
#              metavar='<grpc deadline>', show_default=True,
#              help='gRPC deadline in seconds')
def main(device_model_id, device_id,
    api_endpoint=ASSISTANT_API_ENDPOINT,
    credentials=os.path.join(click.get_app_dir('google-oauthlib-tool'), 'credentials.json'),
    lang='en-US', display=False, verbose=False,
    grpc_deadline=DEFAULT_GRPC_DEADLINE,
    *args,
    **kwargs
):
    # Setup logging.
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)

    # Load OAuth 2.0 credentials.
    try:
        with open(credentials, 'r') as f:
            credentials = google.oauth2.credentials.Credentials(token=None,
                                                                **json.load(f))
            http_request = google.auth.transport.requests.Request()
            credentials.refresh(http_request)
    except Exception as e:
        logging.error('Error loading credentials: %s', e)
        logging.error('Run google-oauthlib-tool to initialize '
                      'new OAuth 2.0 credentials.')
        return

    def query_assistant(text, display: bool):
        nonlocal credentials
        # Create an authorized gRPC channel.
        grpc_channel = google.auth.transport.grpc.secure_authorized_channel(
            credentials, http_request, api_endpoint)
        logging.info('Connecting to %s', api_endpoint)

        with SampleTextAssistant(lang, device_model_id, device_id, display,
                                 grpc_channel, grpc_deadline) as assistant:
            response_text, response_html, full_resp, all_resp_objs, audio_bytes = \
                assistant.assist(text_query=text)
            #if response_text:
            #    click.echo('<@assistant> %s' % response_text)
            #else:
            #    click.echo('<No Response Text>')
            return response_text, response_html, full_resp, all_resp_objs, audio_bytes

    #df = pd.read_csv(cur_file / "../../datatoy/labels/needqueries.csv")
    df = pd.read_csv(cur_file / "../../datatoy/outputs/needqueries.csv")
    col = "Google Assistant Response"
    if col not in df:
        df[col] = ""
    for index, row in list(df.iterrows()):
        print("Index", index)
        text = row.text
        if not pd.isnull(row[col]):
            print("Skiping because already data")
            continue
        #text = "are are you a digital assistant?"
        if str(row.ImpliedExtraContext) != "0":
            continue
        #text = "am i speaking to a live person"
        #text = "am i speaking to a live person"
        row = row.copy()
        #print("index:", index)
        response_text, response_html, full_resp, all_resp_objs, audio_bytes = query_assistant(
            text,
            display=False
        )
        if display and response_html:
            system_browser = browser_helpers.system_browser
            system_browser.display(response_html)
        #print(full_resp)
        #print(type(full_resp))
        #print(dir(full_resp))
        #print(all_resp_objs)
        audio_path = (cur_file / "audioresults")
        audio_path.mkdir(exist_ok=True)
        audio_file = (audio_path / f"{index}.{slugify(text)}.raw")
        audio_file.write_bytes(audio_bytes)
        def play_audio():
             subprocess.run([
                 *("play -t raw -r 16k -e signed -b 16 -c 1").split(),
                 str(audio_file),
                 *("trim 0 00:10").split(),
             ])

        use_text = response_text if response_text is not None else "<NONE>"
        if response_text is None:
            while True:
                print("Query:", text)
                print("TEXT", response_text)
                print("Use Text:", use_text)
                play_audio()
                prompt = click.prompt("(P)lay Again, (C)ontinue, (E)dit:")
                if prompt == "C":
                    break
                if prompt == "P":
                    play_audio()
                if prompt == "E":
                    use_text = "<MANUAL>: " + click.prompt("New Text:")
                    break
        else:
            print("Query:", text)
            print("TEXT", response_text)
            print("Use Text:", use_text)
            print("Add sleep.")
            time.sleep(random.randrange(1, 10))

        df.loc[index, col] = use_text
        df.to_csv(cur_file / "../../datatoy/outputs/needqueries.csv", index=False)
        #print(full_resp)


if __name__ == "__main__":
    config = json.loads((cur_file / "google_config.json").read_text())
    main(
        device_model_id=config['device-model-id'],
        device_id=config["device-id"],
        verbose=False
    )