import unittest
from unittest.mock import patch, mock_open
from config_handler import ConfigHandler

class TestConfigHandler(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data='{"instance": "gitlab.com", "token": "test_token"}')
    def test_load_config_existing(self, mock_file):
        config = ConfigHandler('test1_config.json').load_config()
        self.assertEqual(config, {"instance": "gitlab.com", "token": "test_token"})

    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('builtins.input', side_effect=['gitlab.com', 'test_token'])
    def test_load_config_create_new(self, mock_input, mock_file):
        with patch('json.dump'):
            config = ConfigHandler('test2_config.json').load_config()
            self.assertEqual(config, {"instance": "gitlab.com", "token": "test_token"})