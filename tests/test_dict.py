from incognito_anonymizer import PersonalInfo, anonymizer
import pytest
from datetime import datetime


def test_valid_personal_info():
    # Instance valide
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "birth_name": "Smith",
        "birthdate": datetime(1990, 5, 15),
        "ipp": "123456789",
        "postal_code": "29200",
        "adress": "123 Main Street"
    }
    info = PersonalInfo(**data)

    assert info.first_name == "John"
    assert info.last_name == "Doe"
    assert info.birth_name == "Smith"
    assert info.birthdate == datetime(1990, 5, 15)
    assert info.ipp == "123456789"
    assert info.postal_code == "29200"
    assert info.adress == "123 Main Street"


def test_from_dict_valid_data():
    # Transformation d'un dictionnaire valide
    data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "birth_name": "Johnson",
        "birthdate": datetime(1985, 8, 25),
        "ipp": "987654321",
        "postal_code": "75001",
        "adress": "456 Elm Street"
    }

    info = PersonalInfo(**data)
    assert info.first_name == "Jane"
    assert info.last_name == "Doe"
    assert info.birth_name == "Johnson"
    assert info.birthdate == datetime(1985, 8, 25)
    assert info.ipp == "987654321"
    assert info.postal_code == "75001"
    assert info.adress == "456 Elm Street"


def test_from_dict_missing_name():
    # Transformation d'un dictionnaire valide
    data = {
        "first_name": "Jane",
        "last_name": None,
        "birth_name": "Johnson",
        "birthdate": datetime(1985, 8, 25),
        "ipp": "987654321",
        "postal_code": "75001",
        "adress": "456 Elm Street"
    }
    ano = anonymizer.Anonymizer()
    info = ano.set_info_from_dict(**data)
    assert info.first_name == "Jane"
    assert info.last_name == ""
    assert info.birth_name == "Johnson"
    assert info.birthdate == datetime(1985, 8, 25)
    assert info.ipp == "987654321"
    assert info.postal_code == "75001"
    assert info.adress == "456 Elm Street"


def test_from_dict_full_date():
    # Transformation d'un dictionnaire valide
    data = {
        "first_name": "Jane",
        "last_name": None,
        "birth_name": "Johnson",
        "birthdate": datetime(1985, 8, 25, 0, 0, 0),
        "ipp": "987654321",
        "postal_code": "75001",
        "adress": "456 Elm Street"
    }
    ano = anonymizer.Anonymizer()
    info = ano.set_info_from_dict(**data)
    assert info.first_name == "Jane"
    assert info.last_name == ""
    assert info.birth_name == "Johnson"
    assert info.birthdate == datetime(1985, 8, 25)
    assert info.ipp == "987654321"
    assert info.postal_code == "75001"
    assert info.adress == "456 Elm Street"


def test_from_dict_missing_data():
    # Transformation avec données manquantes
    data = {
        "first_name": "Alice",
        "last_name": "Wonderland"
        # Les autres champs sont absents
    }
    info = PersonalInfo(**data)

    assert info.first_name == "Alice"
    assert info.last_name == "Wonderland"
    assert info.birth_name == ""
    assert info.birthdate == datetime(1000, 1, 1)
    assert info.ipp == ""
    assert info.postal_code == "0"
    assert info.adress == ""


def test_validation_error():
    # Données invalides
    with pytest.raises(ValueError):
        PersonalInfo(
            first_name="John",
            last_name="Doe",
            birthdate="invalid_date",  # Date invalide
            ipp="123456789"
        )
