import unittest
from unittest.mock import MagicMock, patch
from diff_handler import DiffHandler

class TestDiffHandler(unittest.TestCase):
    def setUp(self):
        self.git_handler = MagicMock()
        self.gitlab_handler = MagicMock()
        self.diff_handler = DiffHandler(self.gitlab_handler, self.git_handler)

    def test_is_stacked(self):
        self.assertTrue(self.diff_handler.is_stacked('origin/feature-123-abc123'))
        self.assertFalse(self.diff_handler.is_stacked('origin/main'))

    def test_group_stacked_diffs(self):
        self.gitlab_handler.get_mr_info.return_value = {
            'author': 'Test User',
            'iid': 1,
            'created_at': '2023-01-01T00:00:00Z'
        }
        branches = ['origin/feature-123-abc123', 'origin/feature-123-def456']
        result = self.diff_handler.group_stacked_diffs(branches)
        self.assertEqual(len(result), 1)

    @patch('subprocess.run')
    @patch('json.dump')
    def test_create_stack_json(self, mock_json_dump, mock_subprocess_run):
        branches_info = [('origin/feature-123-abc123', 1, '2023-01-01T00:00:00Z')]

        self.git_handler.extract_sha_from_branch_name.return_value = 'abc123'
        self.git_handler.get_gitlab_url.return_value = 'https://gitlab.com/test/repo'
        self.git_handler.get_branch_sha.return_value = 'abc123'
        self.gitlab_handler.get_mr_description.return_value = 'Test description'

        with patch('pathlib.Path.open', MagicMock()):
            self.diff_handler.create_stack_json(branches_info, 'feature-123 (Test User)')

        mock_subprocess_run.assert_called_once()
        mock_json_dump.assert_called_once()

