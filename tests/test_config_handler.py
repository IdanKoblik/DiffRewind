import unittest
from unittest.mock import patch, mock_open
from src.config_handler import ConfigHandler

class TestConfigHandler(unittest.TestCase):
    def setUp(self):
        self.config_handler = ConfigHandler('test_config.json')

    @patch('builtins.open', new_callable=mock_open, read_data='{"instance": "gitlab.com", "token": "test_token"}')
    def test_load_config_existing(self, mock_file):
        config = self.config_handler.load_config()
        self.assertEqual(config, {"instance": "gitlab.com", "token": "test_token"})

    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('builtins.input', side_effect=['gitlab.com', 'test_token'])
    def test_load_config_create_new(self, mock_input, mock_file):
        with patch('json.dump'):
            config = self.config_handler.load_config()
            self.assertEqual(config, {"instance": "gitlab.com", "token": "test_token"})