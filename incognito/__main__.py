from . import cli
from . import analyzer
from . import anonymizer
import sys
ano_cli = cli.AnonymiserCli()
test = anonymizer.Anonymizer()
if __name__ == '__main__':
    # ano_cli.run(argv=sys.argv[1:])
    # results = test.multi_subs_by_regex(
    #     'hi! peoples',
    #     {'hi': 'hello', 'p[a-z]+s': 'world'}
    # )
    # print(results)
    test.set_strategies(['regex'])
    test.set_masks(['fake'])
    # text = test.open_text_file(
    #     '/data/homes/arthur/incognito/docs/docselect/0069914276.txt')
    text = "bonjour monsieur JEAN Jean, voici votre email : jean.jean@gmail.com"
    output = test.anonymize(text)
    print("Anonymized texte : ", output)
