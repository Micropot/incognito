import pytest
from unittest.mock import patch, MagicMock
from incognito.cli import AnonymiserCli


def test_parse_cli_valid_args():
    """Teste si parse_cli retourne les bons arguments avec des arguments valides."""
    argv = [
        "--input", "input.txt",
        "--output", "output.txt",
        "--strategies", "regex", "pii",
        "--mask", "placeholder",
        "--verbose",
        "json",
        "--json", "infos.json"
    ]

    cli = AnonymiserCli()
    args = cli.parse_cli(argv)

    # Vérifie les valeurs retournées
    assert args.input == "input.txt"
    assert args.output == "output.txt"
    assert args.strategies == ["regex", "pii"]
    assert args.mask == ["placeholder"]
    assert args.verbose is True
    assert args.command == "json"
    assert args.json == ["infos.json"]


def test_parse_cli_missing_required_args():
    """Teste si parse_cli échoue correctement sans les arguments requis."""
    argv = [
        "--output", "output.txt",  # Manque --input
        "infos",
        "--first_name", "John",
        "--last_name", "Doe",
        "--birthdate", "1990-01-01",
        "--ipp", "123456"
    ]

    cli = AnonymiserCli()

    with pytest.raises(SystemExit) as excinfo:
        cli.parse_cli(argv)
    assert excinfo.type == SystemExit
    assert excinfo.value.code == 2  # Code 2 pour erreur d'arguments argparse


def test_parse_cli_subcommand_infos():
    """Teste le comportement avec la sous-commande 'infos'."""
    argv = [
        "--input", "input.txt",
        "--output", "output.txt",
        "infos",
        "--first_name", "Alice",
        "--last_name", "Smith",
        "--birthdate", "1992-03-04",
        "--ipp", "7891011",
        "--postal_code", "75001",
        "--adress", "1 Rue Exemple"
    ]

    cli = AnonymiserCli()
    args = cli.parse_cli(argv)

    # Vérifie que les valeurs des sous-commandes sont correctement interprétées
    assert args.first_name == "Alice"
    assert args.last_name == "Smith"
    assert args.birthdate == "1992-03-04"
    assert args.ipp == "7891011"
    assert args.postal_code == "75001"
    assert args.adress == "1 Rue Exemple"


def test_run_valid_args():
    """Teste si run fonctionne correctement avec des arguments valides."""
    argv = [
        "--input", "input.txt",
        "--output", "output.txt",
        "--verbose",
        "json",
        "--json", "infos.json"
    ]

    with patch("incognito.cli.anonymizer.Anonymizer") as MockAnonymizer:
        mock_ano_instance = MagicMock()
        MockAnonymizer.return_value = mock_ano_instance

        mock_ano_instance.open_json_file.return_value = {"info": "data"}
        mock_ano_instance.anonymize.return_value = "Texte anonymisé"

        cli = AnonymiserCli()

        with patch("builtins.open", MagicMock()) as mock_file:
            with patch("sys.stdout", new_callable=MagicMock) as mock_stdout:
                cli.run(argv)
            mock_ano_instance.open_text_file.assert_called_with("input.txt")
            mock_ano_instance.anonymize.assert_called_once()
            mock_file.assert_called_once_with("output.txt", "w")
            mock_file.return_value.write.assert_called_once_with(
                "Texte anonymisé")


def test_run_valid_args_json():
    """Teste si run fonctionne correctement avec des arguments valides."""
    argv = [
        "--input", "input.txt",
        "--output", "output.txt",
        "--verbose",
        "json",
        "--json", "infos.json"
    ]

    with patch("incognito.cli.anonymizer.Anonymizer") as MockAnonymizer:
        mock_ano_instance = MagicMock()
        MockAnonymizer.return_value = mock_ano_instance
        mock_ano_instance.open_json_file.return_value = {"info": "data"}
        mock_ano_instance.anonymize.return_value = "Texte anonymisé"

        cli = AnonymiserCli()

        with patch("builtins.open", MagicMock()) as mock_file:
            with patch("sys.stdout", new_callable=MagicMock) as mock_stdout:
                cli.run(argv)

            mock_ano_instance.open_text_file.assert_called_with("input.txt")

            mock_ano_instance.anonymize.assert_called_once()

            mock_file.assert_called_once_with("output.txt", "w")
            mock_file.return_value.write.assert_called_once_with(
                "Texte anonymisé")


def test_run_valid_args_infos():
    """Teste si run fonctionne correctement avec des arguments valides."""
    argv = [
        "--input", "input.txt",
        "--output", "output.txt",
        "--verbose",
        "infos",
        "--first_name", "John",
        "--last_name", "Doe",
        "--birthdate", "1990-01-01",
        "--ipp", "123456"
    ]

    with patch("incognito.cli.anonymizer.Anonymizer") as MockAnonymizer:
        mock_ano_instance = MagicMock()
        MockAnonymizer.return_value = mock_ano_instance

        mock_ano_instance.anonymize.return_value = "Texte anonymisé"

        cli = AnonymiserCli()

        with patch("builtins.open", MagicMock()) as mock_file:
            with patch("sys.stdout", new_callable=MagicMock) as mock_stdout:
                cli.run(argv)

            mock_ano_instance.open_text_file.assert_called_with("input.txt")

            mock_ano_instance.anonymize.assert_called_once()

            mock_file.assert_called_once_with("output.txt", "w")
            mock_file.return_value.write.assert_called_once_with(
                "Texte anonymisé")


def test_run_missing_args():
    """Teste si run échoue avec des arguments manquants."""
    argv = [
        "--output", "output.txt",  # Manque --input
        "infos",
        "--first_name", "John",
        "--last_name", "Doe",
        "--birthdate", "1990-01-01",
        "--ipp", "123456"
    ]

    cli = AnonymiserCli()

    with pytest.raises(SystemExit) as excinfo:
        cli.run(argv)

    assert excinfo.type == SystemExit
    assert excinfo.value.code == 2  # Code 2 pour erreur d'arguments argparse
