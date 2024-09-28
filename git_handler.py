import subprocess
import logging
import configparser
import re
from pathlib import Path

class GitHandler:
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.logger = logging.getLogger(__name__)
        self.git_config = configparser.ConfigParser()

    def is_valid_repo(self):
        return (self.repo_path / '.git').is_dir()

    def get_branches(self):
        try:
            branches = subprocess.check_output(
                ["git", "branch", "-r", "--format=%(refname:short)"],
                cwd=self.repo_path,
                text=True
            )
            return branches.splitlines()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error getting branches: {e}")
            return []

    def get_origin_url(self):
        self.git_config.read(f"{self.repo_path}/.git/config")
        if 'remote "origin"' in self.git_config:
            return self.git_config['remote "origin"'].get('url')
        return None

    def get_gitlab_url(self):
        origin_url = self.get_origin_url()
        if not origin_url:
            return None
        
        ssh_pattern = r'git@(.+?):(.+)'
        match = re.match(ssh_pattern, origin_url)
        
        if match:
            # Convert SSH to HTTPS
            domain = match.group(1)
            repo_path = match.group(2)
            https_url = f'https://{domain}/{repo_path.replace(":", "/")}'
            return https_url

        if origin_url.startswith('http'):
            return origin_url

        return None 

    def extract_sha_from_branch_name(self, branch_name):
        parts = branch_name.split('-')
        if len(parts) > 1:
            return parts[-1]
        return None
    
    def get_git_repo_path(self):
        return f"{self.repo_path}/.git/"
    
    def get_branch_sha(self, branch):
        return subprocess.check_output(
            ["git", "rev-parse", branch], 
            cwd=self.repo_path,
            text=True
        )