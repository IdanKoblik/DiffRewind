import re
import json
from collections import defaultdict
from pathlib import Path
import configparser
import subprocess
from typing import Dict, List, Tuple
from git_handler import GitHandler
from gitlab_handler import GitLabHandler

class DiffHandler:
    STACKED_DIFF_PATTERN = re.compile(r'^origin/[^/]+?-[^-]+-[a-f0-9]+$')

    def __init__(self, gitlab_handler: GitLabHandler, git_handler: GitHandler):
        self.gitlab_handler = gitlab_handler
        self.git_handler = git_handler
        self.config = configparser.ConfigParser()

    def is_stacked(self, branch: str) -> bool:
        return bool(self.STACKED_DIFF_PATTERN.match(branch))

    def group_stacked_diffs(self, branches: List[str]) -> Dict[str, List[Tuple[str, int, str]]]:
        stacked_diffs = defaultdict(list)
        for branch in branches:
            if self.is_stacked(branch):
                mr_info = self.gitlab_handler.get_mr_info(self.gitlab_handler.project_id, branch.replace("origin/", ""))
                if mr_info:
                    base_name = f"{branch.split('-')[0]}-{branch.split('-')[1]} ({mr_info['author']})"
                    stacked_diffs[base_name].append((branch, mr_info['iid'], mr_info['created_at']))
        
        return {k: sorted(v, key=lambda x: x[1]) for k, v in sorted(stacked_diffs.items())}

    def create_stack_json(self, branches_info: List[Tuple[str, int, str]], stack: str) -> None:
        stack_name = stack.split('-')[1].split(' ')[0]
        subprocess.run(["glab", "stack", "create", stack_name], check=True, cwd=self.git_handler.repo_path)

        stack_location = Path(self.git_handler.get_git_repo_path()) / "stacked" / stack_name
        stack_location.mkdir(parents=True, exist_ok=True)

        for i, (branch, iid, created_at) in enumerate(branches_info):
            current_sha = self.git_handler.extract_sha_from_branch_name(branch)
            prev_sha = self.git_handler.extract_sha_from_branch_name(branches_info[i - 1][0]) if i > 0 else ""
            next_sha = self.git_handler.extract_sha_from_branch_name(branches_info[i + 1][0]) if i < len(branches_info) - 1 else ""
            
            mr_description = self.gitlab_handler.get_mr_description(self.gitlab_handler.project_id, iid)
            mr_url = f"{self.git_handler.get_gitlab_url().rstrip('.git')}/-/merge_requests/{iid}"

            self._update_git_config(branch)
            self._create_head_file(branch)

            data = {        
                "prev": prev_sha,
                "branch": branch.replace("origin/", ''),
                "sha": current_sha,
                "next": next_sha,
                "mr": mr_url,
                "description": mr_description
            }

            with (stack_location / f"{current_sha}.json").open('w') as file:
                json.dump(data, file, indent=2)

    def _update_git_config(self, branch: str) -> None:
        config_file = Path(self.git_handler.get_git_repo_path()) / "config"
        self.config.read(config_file)
        self.config[f'branch "{branch.replace("origin/", "")}"'] = {
            "remote": "origin",
            "merge": f"refs/heads/{branch.replace('origin/', '')}"
        }
        with config_file.open('w') as configFile:
            self.config.write(configFile)

    def _create_head_file(self, branch: str) -> None:
        head_file = Path(self.git_handler.get_git_repo_path()) / "refs" / "heads" / branch.replace("origin/", '')
        head_file.parent.mkdir(parents=True, exist_ok=True)
        head_file.write_text(self.git_handler.get_branch_sha(branch))
