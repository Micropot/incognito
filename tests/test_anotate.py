from incognito_anonymizer import anonymizer


def test_standoff():
    ano = anonymizer.Anonymizer()
    ano.set_annotator('standoff')
    ano.add_analyzer('regex')
    input_text = "Dr. Bob"
    output_text = ano.annotate(input_text)
    assert output_text == "T1\tNAME 4 7\tBob"
