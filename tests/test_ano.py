from incognito import Anonymizer
import pytest

dataset = {

    "phone": ("tél: 0651565600","tél: <PHONE>" ),
    "phone1": ("tél: 0651565600","tél: <PHONE>" ),
    "phone2": ("tél: 0651565600","tél: <PHONE>" ),
    
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
