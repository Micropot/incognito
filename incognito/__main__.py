from . import cli
import sys
ano_cli = cli.AnonymiserCli()
if __name__ == '__main__':
    ano_cli.run(argv=sys.argv[1:])
