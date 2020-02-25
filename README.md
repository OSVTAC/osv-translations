# Open Source Voting Translation Manager (OTM)

Contains translations of phrases occurring in TAC's results templates
and scripts to manage those translations.

The YAML files in this repo are meant to be edited by hand.

The `translations.json` file is the main artifact that this repo
exposes for external use.  It is machine-readable and for use in
results reports.


## Usage

```
python manage.py CMD
```

To update / regenerate the `translations.json` file:

```
python manage.py build_json
```
