
## Description
Incognitio is a module for french text anonymization. The goal of this module is to anonymize text with Regex to mask all the names and personal information given by the user.
Since this module was developed for medical reports, the diseases name are kept.


[![python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)

## Installation
### From this repositry
1. Clone the repository
    ```bash
    git clone https://github.com/Micropot/incognito
    ```
2. Install the the dependances (. because dependances are definded in the pyproject.toml)
     ```bash
     pip install . 
     ```


## Usage
### Python
With personal infos in the code : 
```python
from . import anonymizer
ano = anonymizer.Anonymizer()
infos = {
    "first_name": "Bob",
    "last_name": "Jungels",
    "birth_name": "",
    "birthdate": "1992-09-22",
    "ipp": "0987654321",
    "postal_code": "01000",
    "adress": ""
}
ano.set_info(infos)
ano.set_strategies(['regex', 'pii'])
ano.set_masks('placeholder')
text_to_anonymize = ano.open_text_file("/path/to/file.txt")
anonymized_text = ano.anonymize(text_to_anonymize)
print(anonymized_text)
```
With infos in json file : 
```python
from . import anonymizer
ano = anonymizer.Anonymizer()
infos_json = ano.open_json_file("/path/to/infofile.json")
ano.set_info(infos_jsons)
ano.set_strategies(['regex', 'pii'])
ano.set_masks('placeholder')
text_to_anonymize = ano.open_text_file("/path/to/file.txt")
anonymized_text = ano.anonymize(text_to_anonymize)
print(anonymized_text)
```
### CLI
#### Mandatory arguments for each method : 
```bash
python -m incognito --input myinputfile.txt --output myanonymizedfile.txt --strategies mystrategies --mask mymasks
```
Available strategies and masks can be found eather in the source code or in the cli helper. 
```bash
python -m incognito --help
```
#### Anonymizer with json file
```bash
python -m incognito --input myinputfile.txt --output myanonymizedfile.txt --strategies mystrategies --mask mymasks json --json myjsonfile.json
```
Helper for the json submodule : 
```bash
python -m incognito --input myinputfile.txt --output myanonymizedfile.txt --strategies mystrategies --mask mymasks json --help
```

#### Anonymizer with personal infos directly in CLI
```bash
python -m incognito --input myinputfile.txt --output myanonymizedfile.txt --strategies mystrategies --mask mymasks infos --first_name Bob --last_name Dylan --birthdate 1800-01-01 --ipp 0987654312 --postal_code 75001
```
Helper for the infos submodule : 
Useful for knowing any optional arguments.
```bash
python -m incognito --input myinputfile.txt --output myanonymizedfile.txt --strategies mystrategies --mask mymasks infos --help
```

### Python

```python
from . import anonymizer

ano = anonymzier.Anonymizer()
personal_infos = {
    "first_name": "Bob",
    "last_name": "Jungels",
    "birth_name": "",
    "birthdate": "1992-09-22",
    "ipp": "0987654321",
    "postal_code": "01000",
    "adress": ""
}
ano.set_info(infos=personal_infos)
ano.set_strategies(['regex', 'pii'])
ano.set_masks('placeholder')
text_to_anonymize = ano.open_text_file("/path/to/my/file.txt")
anonymized_text = ano.anonymize(text_to_anonymize)
print(anonymized_text)

```
### Unittests
Unittest are included in this module. They are testing all the functions and can be modified depending on the needs.

To run unittests : 
```bash
make test
```

To run code coverage : 
```bash
make cov
```
## Informations about the anonymization process
### Regex
One of the avalaible strategy is regex anonymisation. This one can extract specific informations for the input text such as email adresses, phone numbers, NIR (french security number), first and last name <b>if preceded by Monsieur, Madame, Mr, Mme, Docteur, Professeur, etc...</b> (see [`RegexStrategy Class`](https://github.com/Micropot/incognito/blob/main/incognito/analyzer.py), self.title_regex variable).




