Code for the R-U-A-Robot Dataset.

We use Python 3.8.5, but will probably work on Python 3.6+.
Start with installing the requirements in requirements.txt.

Highlights:

* datatoy/create_dataset_files.py - This is the main file used for creating sampling the grammar and making the splits
* baselines/runbaselines.py - Used to run baselines and grammar baselines on the models.
    It will print a latex table at the end. Note though, seeds aren't fixed. If you run it
    expect some variance in underlying numbers. The ranking between models should be pretty
    stable though.
* templates/areyourobot_grammar.py - Grammar for positive examples. Executing it should print 100 samples.
* templates/distractor_grammar.py - Grammar for hard negatives
* templates/ambigious_grammar.py - Grammar for AIC examples

Other somewhat useful files:

* classify_text_plz - Actual code the ML model baselines. 
    Useful if really want to dig into exact details of hyperparameters. We used fairly default/typical settings.
* datatoy/check_grammar_coverage.py - Used as a test to if grammar fully covers the data we collect from
    the Turk data, the Tf-IDF data, and the rand data.
* templates/gramdef.py - The backend logic of the Context Free Grammar
* datatoy/modifiers.py - The modifier helps with augmenting/allowing typos in the context free grammar
* othersurvey/responsecats.py - How we made the questions for the "good response" surveys
* tests - About 35 automated tests for the CFG, utilities, and fancy within-rule partitioning stuff.
* datatoy/grammar_classifier.py - How we convert our classifier. See also:
    * templates/gramgen.py - converts the grammar into EBNF form for use in a off the shelf parser (Lark).
        Also the GramRecognizer is the backend of the classifier and includes some of 
        the heuristics we mention in the paper.

In the data files we provide the existing system outputs (blender, Alexa, Google), but here's how we get them:

* baselines/blender_baseline - Code for getting blender responses to possitive examples
* baselines/googleassistant/google_assistant_run.py - Get google assistant results
* baselines/googleassistant/audioresults - The audio results because some results in the spreadsheet were truncated transcriptions
Unforunately Alexa was a manual process in the Alexa simulator.