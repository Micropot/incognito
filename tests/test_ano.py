from incognito import Anonymizer
from incognito import analyzer
from incognito import mask
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
    "P._NOM": ("J. Jean", "J. Jean"),
    "Monsieur_NOM_Prenom": ("Monsieur KEAN Jean", "Monsieur <NAME>"),
    "Monsieur_NOM_Prenom_DOUBLE": ("Monsieur KEAN KEZAN Jean-Baptiste", "Monsieur <NAME>"),
    "INTERNE_NOM-NOM_Prenom": ("name : Interne : DE-TROIS Jean", "name : Interne : <NAME>"),
    "Titre_Interne": ("Interne", "Interne"),
    "Docteur_NOM_Prenom": ("Docteur DUPONT Jean", "Docteur <NAME>"),
    "Monsieur_P._NOM": ("Monsieur J. Jean", "Monsieur <NAME>"),
    "Dr_NOM_Prenom": ("Dr LECLERC Charle", "Dr <NAME>"),
    "DR._NOM": ("DR. LECLERC", "DR. <NAME>"),
    "Interne_NOM_Prenom": ("Interne JEAN Jean", "Interne <NAME>"),
    "Externe_NOM_Prenom": ("Externe JEAN Jean", "Externe <NAME>"),
    "nom_phone": ("Monsieur JEAN Lasalle, tél : 0647482884", "Monsieur <NAME>, tél : <PHONE>"),
    "double_nom": ("Monsieur JEAN Jean, Docteur Jeanj JEAN, Madame JEANNE Jean", "Monsieur <NAME>, Docteur <NAME>, Madame <NAME>"),
    "test": ("Bonjour Monsieur JEAN Jean, voici son numéro : 0606060606 et son email jean.jean@gmail.fr", "Bonjour Monsieur <NAME>, voici son numéro : <PHONE> et son email <EMAIL>"),
    "née_madame": ("Madame DUPONT Mariane née MORGAT", "Madame <NAME> née <NAME>"),
    "né_monsieur": ("Monsieur J. Jean né LA RUE", "Monsieur <NAME> né <NAME>")
}


datas_regex = list(dataset_regex.values())
ids_regex = list(dataset_regex.keys())


@ pytest.mark.parametrize(
    "input,output", datas_regex, ids=ids_regex
)
def test_regex_strategie(input, output):

    ano = Anonymizer()
    ano.set_strategies(['regex'])
    ano.set_masks('placeholder')
    assert ano.anonymize(input) == output


infos = {
    "first_name": "Bob",
    "last_name": "Jungels",
    "birth_name": "",
    "birthdate": "1992-09-22",
    "ipp": "0987654321",
    "postal_code": "01000",
    "adress": ""
}

dataset_pii = {
    "Nom_Prenom_PII": ("Bob Jungels", "<NAME> <NAME>"),
    "Date_IPP_Postal": ("1992-09-22 0987654321 01000", "<DATE> <IPP> <CODE_POSTAL>")
}

datas_pii = list(dataset_pii.values())
ids_pii = list(dataset_pii.keys())


@ pytest.mark.parametrize(
    "input,output", datas_pii, ids=ids_pii
)
def test_pii_strategie(input, output):

    ano = Anonymizer()
    ano.set_info(infos)
    ano.set_strategies(['pii'])
    ano.set_masks('placeholder')
    assert ano.anonymize(input) == output


def test_anaylser_not_implemented_error():
    with pytest.raises(NotImplementedError):
        analyzer.Strategy.analyze(text="test")


def test_mask_not_implemented_error():
    with pytest.raises(NotImplementedError):
        mask.Strategy.mask("test", coordinate=((10, 10), "<TEST>"))
