from . import anonymizer
import sys


ano = anonymizer.Anonymizer()
# ano = ano.run_dummy_algorithm(text=text, info=infos)
if __name__ == '__main__':
    ano.anonymize()
    # test = ano.run(argv=sys.argv[1:])
