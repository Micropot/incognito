import argparse
from . import anonymizer


class AnonymiserCli:
    """Class pour utiliser le CLI"""

    @staticmethod
    def parse_cli(argv):
        parser = argparse.ArgumentParser(description=__doc__)

        parser.add_argument(
            "--input",
            "--input_file",
            type=str,
            help="Chemin du fichier à anonymiser.",
            required=True,
        )
        parser.add_argument(
            "--output",
            "--output_file",
            type=str,
            help="Chemin du fichier de sortie.",
            required=True,
        )

        parser.add_argument(
            "-s",
            "--strategies",
            type=str,
            help="Stratégies à utiliser (default : %(default)s).",
            default=["regex", "pii"],
            nargs="*",
            choices=[key for key, val in anonymizer.Anonymizer.STRATEGIES.items()],
        )
        parser.add_argument(
            "-m",
            "--mask",
            type=str,
            help="Mask à utiliser (default : %(default)s).",
            default=["placeholder"],
            nargs=1,
            choices=[key for key, val in anonymizer.Anonymizer.MASKS.items()],
            required=False,
        )

        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Affiche des messages détaillés pendant l'exécution.",
        )

        # subparser pour les différences entre  json et infos dans le cli
        subparser = parser.add_subparsers(
            dest="command",
            required=True,
            help="Choix entre un fichier JSON, informations patient dans le CLI ou anonymisation par informations par défaut",
        )

        json_parser = subparser.add_parser("json", help="Fournir un fichier JSON")
        json_parser.add_argument(
            "--json",
            "--json_file",
            type=str,
            help="Chemin du fichier json d'information.",
            required=False,
            nargs=1,
        )

        info_parser = subparser.add_parser("infos", help="Fournir infos partients dans le CLI")
        info_parser.add_argument("--first_name", type=str, help="Prénom du patient.", required=True)
        info_parser.add_argument("--last_name", type=str, help="Nom du patient.", required=True)
        info_parser.add_argument(
            "--birthname", type=str, help="Nom de naissance du patient.", required=False, default=""
        )
        info_parser.add_argument(
            "--birthdate", type=str, help="Date de naissance du patient.", required=True
        )
        info_parser.add_argument("--ipp", type=str, help="IPP du patient.", required=True)
        info_parser.add_argument(
            "--postal_code", type=str, help="Code postal du patient.", required=False, default=""
        )
        info_parser.add_argument(
            "--adress", type=str, help="Adresse postal du patient.", required=False, default=""
        )

        return parser.parse_args(argv)

    def run(self, argv):
        """Fonction principal du projet"""
        args = self.parse_cli(argv)
        input_file = args.input
        command = args.command
        output_file = args.output
        strats = args.strategies
        mask = args.mask
        verbose = args.verbose
        ano = anonymizer.Anonymizer()

        if command == "json":
            print("JSON")
            json_file = args.json
            infos = ano.open_json_file(json_file[0])
            ano.infos = ano.set_info(infos)
            print(ano.infos)
        ano.text = ano.open_text_file(input_file)

        if command == "infos":
            first_name = args.first_name
            last_name = args.last_name

            birthname = args.birthname
            birthdate = args.birthdate
            ipp = args.ipp
            postal_code = args.postal_code
            adress = args.adress
            keys = [
                "first_name",
                "last_name",
                "birth_name",
                "birthdate",
                "ipp",
                "postal_code",
                "adress",
            ]
            values = [first_name, last_name, birthname, birthdate, ipp, postal_code, adress]
            infos_dict = {key: value for key, value in zip(keys, values)}
            ano.infos = ano.set_info(infos_dict)
        ano.set_strategies(strats)
        ano.set_masks(mask[0])

        if verbose:
            print("Texte sans anonymisation : ", ano.text)
            print("strategies utilisées : ", strats)
        anonymized_text = ano.anonymize(text=ano.text)
        output = open(output_file, "w")
        output.write(anonymized_text)
        output.close()

        if verbose:
            print("Texte anonymisé : ", anonymized_text)
            print("Texte enregistré ici : ", output_file)
            print("------ Terminé ------")
