import unittest
from datetime import date
from period_tracker import data
from unittest.mock import mock_open, patch
from pathlib import Path
import json


class TestDataModule(unittest.TestCase):
    def setUp(self):
        self.sample_start = date(2024, 6, 1)
        self.duration = 5
        self.sample_entry = {"start": "2024-06-01", "end": "2024-06-05"}
        self.test_data_file = Path("/tmp/fake_data.json")
        data.set_data_file(self.test_data_file)

    @patch("period_tracker.data.encrypt_data_file")
    @patch("builtins.open", new_callable=mock_open)
    def test_write_entries(self, mock_file, mock_encrypt):
        entries = [self.sample_entry]
        data.write_entries(entries)
        mock_file.assert_called_once_with(
            self.test_data_file.with_suffix(""), "w", encoding="utf-8"
        )
        handle = mock_file()
        written = json.loads(
            "".join([call.args[0] for call in handle.write.call_args_list])
        )
        self.assertEqual(written, entries)
        mock_encrypt.assert_called_once_with(self.test_data_file.with_suffix(""))

    @patch("period_tracker.data.decrypt_data_file")
    @patch("pathlib.Path.unlink")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='[{"start": "2024-06-01", "end": "2024-06-05"}]',
    )
    @patch("pathlib.Path.exists", return_value=True)
    def test_load_entries(self, mock_exists, mock_file, mock_unlink, mock_decrypt):
        entries = data.load_entries()
        self.assertEqual(entries, [self.sample_entry])
        mock_decrypt.assert_called_once()
        mock_unlink.assert_called_once()

    def test_create_entry(self):
        entry = data.create_entry(self.sample_start, self.duration)
        self.assertEqual(entry, self.sample_entry)
