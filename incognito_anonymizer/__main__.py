from . import cli
from . import anonymizer
import sys
ano_cli = cli.AnonymiserCli()
test = anonymizer.Anonymizer()
if __name__ == '__main__':
    ano_cli.run(argv=sys.argv[1:])
