import re
import json
from collections import defaultdict
from pathlib import Path
import configparser
import subprocess
import os

class DiffHandler:
    def __init__(self, gitlab_handler, git_handler):
        self.gitlab_handler = gitlab_handler
        self.git_handler = git_handler
        self.config = configparser.ConfigParser()

    def is_stacked(self, branch):
        stacked_diff_pattern = re.compile(r'^origin/[^/]+?-[^-]+-[a-f0-9]+$')
        return stacked_diff_pattern.match(branch)

    def group_stacked_diffs(self, branches):
        stacked_diffs = defaultdict(list)
        for branch in branches:
            if self.is_stacked(branch):
                mr_info = self.gitlab_handler.get_mr_info(self.gitlab_handler.project_id, branch.replace("origin/", ""))
                if mr_info:
                    base_name = f"{branch.split('-')[0]}-{branch.split('-')[1]} ({mr_info['author']})"
                    stacked_diffs[base_name].append((branch, mr_info['iid'], mr_info['created_at']))
        
        # Sort branches within each group by MR IID (first to last order)
        for base_name in stacked_diffs:
            stacked_diffs[base_name].sort(key=lambda x: x[1])
        
        return dict(sorted(stacked_diffs.items()))

    def create_stack_json(self, branches_info, stack):
        subprocess.run(f"glab stack create {stack.split('-')[1].split(' ')[0]}", shell=True, cwd=self.git_handler.get_git_repo_path().replace(".git/", ''))

        stack_location = Path(f"{self.git_handler.get_git_repo_path()}/stacked/{stack.split('-')[1].split(' ')[0]}/")
        stack_location.mkdir(parents=True, exist_ok=True)

        for i, (branch, iid, created_at) in enumerate(branches_info):
            current_sha = self.git_handler.extract_sha_from_branch_name(branch)
            prev_sha = self.git_handler.extract_sha_from_branch_name(branches_info[i - 1][0]) if i > 0 else ""
            next_sha = self.git_handler.extract_sha_from_branch_name(branches_info[i + 1][0]) if i < len(branches_info) - 1 else ""
            mr_description = self.gitlab_handler.get_mr_description(self.gitlab_handler.project_id, iid)
            mr_url = f"{self.git_handler.get_gitlab_url().replace('.git', '')}/-/merge_requests/{iid}"

            config_file = f"{self.git_handler.get_git_repo_path()}/config"
            self.config.read(config_file)
            self.config[f'branch "{branch.replace("origin/", '')}"'] = {
                "remote": "origin",
                "merge": f"refs/heads/{branch.replace("origin/", '')}"
            }

            with open(config_file, 'w') as configFile:
                self.config.write(configFile)

            head = f"{self.git_handler.get_git_repo_path()}refs/heads/{branch.replace("origin/", '')}"
            with open(head, 'x') as head_file:
                head_file.write(self.git_handler.get_branch_sha(f"{branch}"))

            data = {        
                "prev": prev_sha,
                "branch": branch.replace("origin/", ''),
                "sha": current_sha,
                "next": next_sha,
                "mr": mr_url,
                "description": mr_description
            }

            with open(stack_location / f"{current_sha}.json", 'w') as file:
                print(stack_location)
                json.dump(data, file)