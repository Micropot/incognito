from incognito import Anonymizer


def test_hide_person():
    data = {
  "first_name" : "Arthur",
  "last_name" : "Lamard",
  "birth_name" : "",
  "birthdate" : "2000-07-12",
  "ipp" : "0987654321",
  "postal_code" : "29820",
  "adress" : ""
}


    ano = Anonymizer()
    ano.set_info(data)
    ano.used_strats = ['regex', 'pii']
    ano.anonymize("test")
