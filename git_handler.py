import subprocess
import logging
import configparser
import re
from pathlib import Path
from typing import List, Optional

class GitHandler:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.logger = logging.getLogger(__name__)
        self.git_config = configparser.ConfigParser()

    def is_valid_repo(self) -> bool:
        return (self.repo_path / '.git').is_dir()

    def get_branches(self) -> List[str]:
        try:
            result = subprocess.run(
                ["git", "branch", "-r", "--format=%(refname:short)"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.splitlines()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error getting branches: {e}")
            return []

    def get_origin_url(self) -> Optional[str]:
        self.git_config.read(self.repo_path / ".git" / "config")
        return self.git_config.get('remote "origin"', 'url', fallback=None)

    def get_gitlab_url(self) -> Optional[str]:
        origin_url = self.get_origin_url()
        if not origin_url:
            return None
        
        ssh_pattern = r'git@(.+?):(.+)'
        match = re.match(ssh_pattern, origin_url)
        
        if match:
            domain, repo_path = match.groups()
            return f'https://{domain}/{repo_path.replace(":", "/")}'

        if origin_url.startswith('http'):
            return origin_url

        return None 

    def extract_sha_from_branch_name(self, branch_name: str) -> Optional[str]:
        parts = branch_name.split('-')
        return parts[-1] if len(parts) > 1 else None
    
    def get_git_repo_path(self) -> Path:
        return self.repo_path / ".git"
    
    def get_branch_sha(self, branch: str) -> str:
        result = subprocess.run(
            ["git", "rev-parse", branch], 
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()