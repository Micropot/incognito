from . import anonymizer
import sys


# ano = anonymizer.Anonymizer()
ano_cli = anonymizer.AnonymiserCli()
if __name__ == '__main__':
    # ano.anonymize()
    ano_cli.run(argv=sys.argv[1:])
