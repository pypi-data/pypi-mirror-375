# InSillyClo-cli

Documentation available at http://insillyclo.pages.pasteur.fr/insillyclo-cli

## Install

```shell
#!/bin/bash

virtualenv .venv
# alternative:
# python3 -m venv .venv
source .venv/bin/activate
pip install insillyclo
# alternative:
# pip install insillyclo --index-url https://gitlab.pasteur.fr/api/v4/projects/6917/packages/pypi/simple
```

## Use it

### Get the test data

```shell
git clone git@gitlab.pasteur.fr:hub/insillyclo-cli.git
cd insillyclo-cli/
```

### ... to generate a template

```shell
insillyclo template my-template.xlsx \
                    --name "My template" \
                    --restriction-enzyme-goldengate "BsmBI" \
                    --separator - \
                    --nb-input-parts 4
```

or

```shell
insillyclo template my-template.xlsx \
                    --name "My template" \
                    --enzyme "BsmBI" \
                    --separator - \
                    --input-part ConL \
                    --input-part Promoter \
                    --input-part CDS \
                    --input-part Terminator \
                    --input-part ConR \
                    --input-part Backbone
```

### ... run simulation

```shell
insillyclo simulate --input-template-filled ./tests/data/template_01_mixed_ok.xlsx \
                    --input-parts-file ./tests/data/DB_iP_not_typed.csv \
                    --input-parts-file ./tests/data/DB_iP_typed.csv \
                    --plasmid-repository ./tests/data/plasmids_gb \
                    -o ./output/ \
                    --restriction-enzyme-gel NotI \
                    --primer-pair P84,P134 \
                    --primers-file ./tests/data/primers.csv \
                    --default-mass-concentration 200 \
                    --enzyme-and-buffer-volume 1.0
```
