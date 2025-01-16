from . import cli
from . import anonymizer
ano_cli = cli.AnonymiserCli()
test = anonymizer.Anonymizer()
if __name__ == '__main__':
    # ano_cli.run(argv=sys.argv[1:])
    # results = test.multi_subs_by_regex(
    #     'hi! peoples',
    #     {'hi': 'hello', 'p[a-z]+s': 'world'}
    # )
    # print(results)
    test.set_strategies(['regex', 'pii'])
    test.set_masks('placeholder')
    # text = test.open_text_file(
    #     '/data/homes/arthur/incognito/docs/docselect/0069914276.txt')
    # text = "bonjour monsieur JEAN Jean, voici votre email : jean.jean@gmail.com"
    text = test.open_text_file("/data/homes/arthur/incognito/docs/test.txt")
    text_json = test.open_json_file(
        "/data/homes/arthur/incognito/docs/infos_test.json")
    test.set_info(text_json)
    output = test.anonymize(text)
    print("Anonymized texte : ", output)
