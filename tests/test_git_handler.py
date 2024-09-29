import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from git_handler import GitHandler

class TestGitHandler(unittest.TestCase):
    def setUp(self):
        self.repo_path = Path('/test/repo')
        self.git_handler = GitHandler(self.repo_path)

    def test_is_valid_repo(self):
        with patch.object(Path, 'is_dir', return_value=True):
            self.assertTrue(self.git_handler.is_valid_repo())

    @patch('subprocess.run')
    def test_get_branches(self, mock_run):
        mock_run.return_value = MagicMock(stdout="branch1\nbranch2", returncode=0)
        branches = self.git_handler.get_branches()
        self.assertEqual(branches, ['branch1', 'branch2'])

    @patch('configparser.ConfigParser.read')
    @patch('configparser.ConfigParser.get')
    def test_get_origin_url(self, mock_get, mock_read):
        mock_get.return_value = 'https://gitlab.com/B1trot/testing.git'
        url = self.git_handler.get_origin_url()
        self.assertEqual(url, 'https://gitlab.com/B1trot/testing.git')

    def test_extract_sha_from_branch_name(self):
        sha = self.git_handler.extract_sha_from_branch_name('feature-123-abc123')
        self.assertEqual(sha, 'abc123')

    @patch('subprocess.run')
    def test_get_branch_sha(self, mock_run):
        mock_run.return_value = MagicMock(stdout="abc123\n", returncode=0)
        sha = self.git_handler.get_branch_sha('main')
        self.assertEqual(sha, 'abc123')