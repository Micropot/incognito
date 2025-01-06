from . import anonymizer


text = """
    Bonjour, je suis Arthur Lamard, je suis ingénieur au CDC, né le 07/12/2000, j'ai actuellement 24 ans.
    Je suis venu au CHU pour un rdv médical pour un mal de genou. L'IPP 0987654321 m'a été attribué. 
    je vis à Guilers, 29820. 
    je suis contactable aux coordonnées suivantes : 
    email: arthur@lamard.org 
    telephone : 0647187486

    
"""


infos = {
    "first_name": "Arthur",
    "last_name": "Lamard",
    "birth_name": "",
    "birthdate": "2000-12-07",
    "ipp": "0987654321",
    "postal_code": "29820"

}
ano = anonymizer.Anonymizer(text=text, infos=infos)
# ano = ano.run_dummy_algorithm(text=text, info=infos)
if __name__ == '__main__':
    test = ano.anonymize_text()
