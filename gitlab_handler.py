import requests
import logging
import re
from typing import Dict, Optional

class GitLabHandler:
    def __init__(self, instance: str, token: str):
        self.instance = instance
        self.token = token
        self.logger = logging.getLogger(__name__)
        self.project_id: Optional[int] = None

    def get_project_id(self, origin_url: str) -> Optional[int]:
        headers = {"PRIVATE-TOKEN": self.token}
        response = requests.get(f"https://{self.instance}/api/v4/projects", headers=headers)
        response.raise_for_status()
        for project in response.json():
            if project['ssh_url_to_repo'] == origin_url or project['http_url_to_repo'] == origin_url:
                return project['id']
        return None

    def get_mr_info(self, project_id: int, branch_name: str) -> Optional[Dict[str, str]]:
        url = f"https://{self.instance}/api/v4/projects/{project_id}/merge_requests?source_branch={branch_name}"
        headers = {"PRIVATE-TOKEN": self.token}

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        mrs = response.json()
        if mrs:
            return {
                "state": mrs[0]["state"],
                "author": mrs[0]["author"]["name"],
                "iid": mrs[0]["iid"],
                "created_at": mrs[0]["created_at"]
            }
        return None

    def get_mr_description(self, project_id: int, iid: int) -> str:
        url = f"https://{self.instance}/api/v4/projects/{project_id}/merge_requests/{iid}"
        headers = {"PRIVATE-TOKEN": self.token}

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("description", "")
