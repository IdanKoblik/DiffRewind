import unittest
from unittest.mock import patch, MagicMock
from gitlab_handler import GitLabHandler

class TestGitLabHandler(unittest.TestCase):
    def setUp(self):
        self.gitlab_handler = GitLabHandler('gitlab.com', 'test_token')

    @patch('requests.get')
    def test_get_project_id(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [{
            'id': 1,
            'path': 'B1trot/testing',
            'ssh_url_to_repo': 'git@gitlab.com:B1trot/testing.git',
            'http_url_to_repo': 'https://gitlab.com/B1trot/testing.git'
        }]
        mock_get.return_value = mock_response
        project_id = self.gitlab_handler.get_project_id('https://gitlab.com/B1trot/testing.git')
        self.assertEqual(project_id, 1)

    @patch('requests.get')
    def test_get_mr_info(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [{
            'state': 'open',
            'author': {'name': 'Test User'},
            'iid': 1,
            'created_at': '2023-01-01T00:00:00Z'
        }]
        mock_get.return_value = mock_response
        mr_info = self.gitlab_handler.get_mr_info(1, 'feature-branch')
        self.assertEqual(mr_info, {
            'state': 'open',
            'author': 'Test User',
            'iid': 1,
            'created_at': '2023-01-01T00:00:00Z'
        })

    @patch('requests.get')
    def test_get_mr_description(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {'description': 'Test description'}
        mock_get.return_value = mock_response
        description = self.gitlab_handler.get_mr_description(1, 1)
        self.assertEqual(description, 'Test description')
