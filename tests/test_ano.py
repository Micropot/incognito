from incognito_anonymizer import Anonymizer
from incognito_anonymizer import analyzer
from incognito_anonymizer import mask
from incognito_anonymizer import PersonalInfo
from datetime import datetime
import pytest

dataset_regex = {

    "phone": ("tél: 0651565600", "tél: <PHONE>"),
    "phone2": ("tél: 06 51 56 56 00", "tél: <PHONE>"),
    "email": ("email : joe.lafripouille@chu-brest.fr", "email : <EMAIL>"),
    "nir": ("nir : 164064308898823", "nir : <NIR>"),
    "NOM_Prenom": ("name : DUPONT Jean", "name : DUPONT Jean"),
    "Prenom_NOM": ("name : Jean DUPONT", "name : Jean DUPONT"),
    "Nom_compose_Prenom": ("name : De La Fontaine Jean", "name : De La Fontaine Jean"),
    "NOM-NOM_Prenom": ("name : DE-TROIS Jean", "name : DE-TROIS Jean"),
    "NOM_accent_Prénom": ("Monsieur JOÉÇ KAKŸÇ", "Monsieur <NAME>"),
    "NOM_accent_prénom": ("Monsieur JOÉÇ Poçèé", "Monsieur <NAME>"),
    "P._NOM": ("J. Jean", "J. Jean"),
    "Monsieur_NOM_Prenom": ("Monsieur KEAN Jean", "Monsieur <NAME>"),
    "Monsieur_NOM_Prenom_DOUBLE": ("Monsieur KEAN KEZAN Jean-Baptiste", "Monsieur <NAME>"),
    "INTERNE_NOM-NOM_Prenom": ("name : Interne : DE-TROIS Jean", "name : Interne : <NAME>"),
    "Titre_Interne": ("Interne", "Interne"),
    "Docteur_NOM_Prenom": ("Docteur DUPONT Jean", "Docteur <NAME>"),
    "Monsieur_P._NOM": ("Monsieur J. Jean", "Monsieur <NAME>"),
    "Dr_NOM_Prenom": ("Dr LECLERC Charle", "Dr <NAME>"),
    "Dr_Prenom_NOM": ("Dr Charle LECLERC", "Dr <NAME>"),
    "DR._NOM": ("DR. LECLERC", "DR. <NAME>"),
    "Interne_NOM_Prenom": ("Interne JEAN Jean", "Interne <NAME>"),
    "Externe_NOM_Prenom": ("Externe JEAN Jean", "Externe <NAME>"),
    "nom_phone": ("Monsieur JEAN Lasalle, tél : 0647482884", "Monsieur <NAME>, tél : <PHONE>"),
    "double_nom": ("Monsieur JEAN Jean, Docteur Jeanj JEAN, Madame JEANNE Jean", "Monsieur <NAME>, Docteur <NAME>, Madame <NAME>"),
    "test": ("Bonjour Monsieur JEAN Jean, voici son numéro : 0606060606 et son email jean.jean@gmail.fr", "Bonjour Monsieur <NAME>, voici son numéro : <PHONE> et son email <EMAIL>"),
    "née_madame": ("Madame DUPONT Mariane née MORGAT", "Madame <NAME> née <NAME>"),
    "né_monsieur": ("Monsieur J. Jean né LA RUE", "Monsieur <NAME> né <NAME>"),
    "test_None": (None, "NaN"),
    "Prof_NOM_PRENOM": ("Professeur JEAN JEAN", "Professeur <NAME>"),
    "Profe_NOM_PRENOM": ("Professeure JEAN JEAN", "Professeure <NAME>"),
    "INT_NOM_PRENOM": ("INT JEAN JEAN", "INT <NAME>"),
    "Date_/": ("01/12/2000", "<DATE>"),
    "Date_-": ("01-12-2000", "<DATE>"),
    "Date_-": ("01-12-2000", "<DATE>"),
    "Date_incorrect": ("12-22-2000", "12-22-2000"),
    "Date_phrase": ("Brest, le 01/01/2000", "Brest, le <DATE>"),
}


datas_regex = list(dataset_regex.values())
ids_regex = list(dataset_regex.keys())


@ pytest.mark.parametrize(
    "input,output", datas_regex, ids=ids_regex
)
def test_regex_strategie(input, output):

    ano = Anonymizer()
    ano.add_analyzer('regex')
    ano.set_mask('placeholder')
    assert ano.anonymize(input) == output


infos = {
    "first_name": "Lea",
    "last_name": "Jungels",
    "birth_name": "",
    "birthdate": datetime(1992, 9, 22, 0, 0, 0),
    "ipp": "0987654321",
    "postal_code": "01000",
    "adress": ""
}
dataset_pii = {
    "Nom_Prenom_PII": ("Léa Jungels", "<NAME> <NAME>"),
    "Date_IPP_Postal": ("22/09/1992 0987654321 01000", "<DATE> <IPP> <CODE_POSTAL>"),
    "DN": ("DN : 22/09/1992 ", "DN : <DATE> ")
}

datas_pii = list(dataset_pii.values())
ids_pii = list(dataset_pii.keys())


@ pytest.mark.parametrize(
    "input,output", datas_pii, ids=ids_pii
)
def test_pii_strategie(input, output):
    ano = Anonymizer()
    ano.set_info_from_dict(**infos)
    ano.add_analyzer('pii')
    ano.set_mask('placeholder')
    assert ano.anonymize(input) == output


def test_anaylser_not_implemented_error():
    with pytest.raises(NotImplementedError):
        analyzer.AnalyzerStrategy.analyze(text="test")


def test_mask_not_implemented_error():
    with pytest.raises(NotImplementedError):
        mask.Strategy.mask("test", coordinate=((10, 10), "<TEST>"))


def test_add_analyser_error():
    ano = Anonymizer()
    with pytest.raises(Exception, match="test analyzer doesn't exist"):
        ano.add_analyzer('test')


def test_set_mask_error():
    ano = Anonymizer()
    with pytest.raises(Exception):
        ano.set_mask('test')


def test_set_annotator_error():
    ano = Anonymizer()
    with pytest.raises(Exception):
        ano.set_annotator('test')
