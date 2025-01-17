import unittest
from unittest.mock import mock_open, patch
import json
from incognito import Anonymizer


class TestFiles(unittest.TestCase):
    def test_open_txt_file_success(self):
        ano = Anonymizer()
        mock_file = "This is a test."

        m = mock_open(read_data=mock_file)

        with patch("builtins.open", m):
            results = ano.open_text_file("test_file.txt")
            self.assertEqual(results, mock_file)

    def test_txt_file_not_found(self):
        ano = Anonymizer()
        with patch("builtins.open", side_effect=FileNotFoundError):
            with self.assertRaises(FileNotFoundError):
                ano.open_text_file("file_not_found.txt")

    def test_open_json_file_success(self):
        ano = Anonymizer()
        mock_file = {"name": "Test"}
        mock_file_str = json.dumps(mock_file)

        m = mock_open(read_data=mock_file_str)

        with patch("builtins.open", m):
            results = ano.open_json_file("test_file.json")
            self.assertEqual(results, mock_file)

    def test_json_file_not_found(self):
        ano = Anonymizer()
        with patch("builtins.open", side_effect=FileNotFoundError):
            with self.assertRaises(FileNotFoundError):
                ano.open_json_file("fichier_inexistant.json")
