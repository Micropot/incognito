
# Incognito

## Description
**Incognito** is a Python module for anonymizing French text. It uses Regex and other strategies to mask names and personal information provided by the user.  
This module was specifically designed for medical reports, ensuring that disease names remain unaltered.

[![python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)

---

## Installation
### From pip
```bash
pip install incognito-anonymizer
```
### From this repository
1. Clone the repository:
    ```bash
    git clone https://github.com/Micropot/incognito
    ```

2. Install the dependencies (defined in `pyproject.toml`):
    ```bash
    pip install .
    ```

---

## Usage

### Python API

#### Example: Providing Personal Information Directly in Code
```python
from . import anonymizer

# Initialize the anonymizer
ano = anonymizer.Anonymizer()

# Define personal information
infos = {
    "first_name": "Bob",
    "last_name": "Jungels",
    "birth_name": "",
    "birthdate": "1992-09-22",
    "ipp": "0987654321",
    "postal_code": "01000",
    "adress": ""
}

# Configure the anonymizer
ano.set_info(infos)
ano.set_strategies(['regex', 'pii'])
ano.set_masks('placeholder')

# Read and anonymize text
text_to_anonymize = ano.open_text_file("/path/to/file.txt")
anonymized_text = ano.anonymize(text_to_anonymize)

print(anonymized_text)
```

#### Example: Using JSON File for Personal Information
```python
from . import anonymizer

# Initialize the anonymizer
ano = anonymizer.Anonymizer()

# Load personal information from JSON
infos_json = ano.open_json_file("/path/to/infofile.json")

# Configure the anonymizer
ano.set_info(infos_json)
ano.set_strategies(['regex', 'pii'])
ano.set_masks('placeholder')

# Read and anonymize text
text_to_anonymize = ano.open_text_file("/path/to/file.txt")
anonymized_text = ano.anonymize(text_to_anonymize)

print(anonymized_text)
```

### Command-Line Interface (CLI)

#### Basic Usage
```bash
python -m incognito --input myinputfile.txt --output myanonymizedfile.txt --strategies mystrategies --mask mymasks
```

#### Find Available Strategies and Masks
```bash
python -m incognito --help
```

#### Anonymization with JSON File
```bash
python -m incognito --input myinputfile.txt --output myanonymizedfile.txt --strategies mystrategies --mask mymasks json --json myjsonfile.json
```

To view helper options for the JSON submodule:
```bash
python -m incognito json --help
```

#### Anonymization with Personal Information in CLI
```bash
python -m incognito --input myinputfile.txt --output myanonymizedfile.txt --strategies mystrategies --mask mymasks infos --first_name Bob --last_name Dylan --birthdate 1800-01-01 --ipp 0987654312 --postal_code 75001
```

To view helper options for the "infos" submodule:
```bash
python -m incognito infos --help
```

---

## Unit Tests

Unit tests are included to ensure the module's functionality. You can modify them based on your needs.

To run the tests:
```bash
make test
```

To check code coverage:
```bash
make cov
```

---

## Anonymization Process Details

### Regex Strategy
One available anonymization strategy is **Regex**. It can extract and mask specific information from the input text, such as:
- Email addresses
- Phone numbers
- French NIR (social security number)
- First and last names (if preceded by titles like "Monsieur", "Madame", "Mr", "Mme", "Docteur", "Professeur", etc.)

For more details, see the [`RegexStrategy` class](incognito/analyzer.py) and the `self.title_regex` variable.

---

## Documentation 
The documentation is available [`here`](https://micropot.github.io/incognito/).

## License

This project is licensed under the terms of the [MIT License](LICENSE).

---

## Contributors

- Maintainer: Micropot  
Feel free to open issues or contribute via pull requests!

