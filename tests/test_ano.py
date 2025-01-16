from incognito import Anonymizer
import pytest

dataset = {

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


datas = list(dataset.values())
ids = list(dataset.keys())


@ pytest.mark.parametrize(
    "input,output", datas, ids=ids
)
def test_regex_strategie(input, output):

    ano = Anonymizer()
    ano.set_strategies(['regex'])
    ano.set_masks('placeholder')
    assert ano.anonymize(input) == output
