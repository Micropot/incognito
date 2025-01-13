from incognito import Anonymizer
import pytest

dataset = {

    "phone": ("tél: 0651565600", "tél: <PHONE>"),
    "email": ("email : joe.lafripouille@chu-brest.fr", "email : <EMAIL>"),
    "nir": ("nir : 164064308898823", "nir : <NIR>"),
    "NOM_Prenom": ("name : DUPONT Jean", "name : DUPONT Jean"),
    "Prenom_NOM": ("name : Jean DUPONT", "name : Jean DUPONT"),
    "Nom_compose_Prenom": ("name : De La Fontaine Jean", "name : De La Fontaine Jean"),
    "NOM-NOM_Prenom": ("name : DE-TROIS Jean", "name : DE-TROIS Jean"),
    "INTERNE_NOM-NOM_Prenom": ("name : Interne : DE-TROIS Jean", "name : <NAME>"),
    "Titre": ("Docteur ", "<TITLE>"),
    "Titre_Interne": ("Interne", "Interne"),
    "Docteur_NOM_Prenom": ("Docteur DUPONT Jean", "<NAME>"),
    "Monsieur_P._NOM": ("Monsieur J. Jean", "<NAME>"),
    "P._NOM": ("J. Jean", "J. Jean"),
    "Dr_NOM_Prenom": ("Dr LECLERC Charle", "<NAME>"),
    "DR._NOM": ("DR. LECLERC", "<NAME>"),
    "Interne_NOM_Prenom": ("Interne JEAN Jean", "<NAME>"),
    "Externe_NOM_Prenom": ("Externe JEAN Jean", "<NAME>"),
}


datas = list(dataset.values())
ids = list(dataset.keys())


@pytest.mark.parametrize(
    "input,output", datas, ids=ids
)
def test_regex_strategie(input, output):

    ano = Anonymizer()
    ano.used_strats = ['regex']

    assert ano.anonymize(input) == output
