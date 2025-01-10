from incognito import Anonymizer
import pytest

dataset = {

    "phone": ("tél: 0651565600","tél: <PHONE>" ),
    "emain": ("email : arthur.lamard@chu-brest.fr","email : <EMAIL>" ),
    "nir": ("nir : 164064308898823","nir : <NIR>" ),
    
}


datas = list(dataset.values())
ids = list(dataset.keys())


@pytest.mark.parametrize(
    "input,output", datas, ids = ids
)
def test_regex_strategie(input, output):


    ano = Anonymizer()
    ano.used_strats = ['regex']

    assert ano.anonymize(input) == output
