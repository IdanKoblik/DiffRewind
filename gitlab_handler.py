import requests
import logging
import re

class GitLabHandler:
    def __init__(self, instance, token):
        self.instance = instance
        self.token = token
        self.logger = logging.getLogger(__name__)

    def get_project_id(self, origin_url):
        project_name = self.get_project_name(origin_url)
        headers = {"PRIVATE-TOKEN": self.token}
        response = requests.get(f"https://{self.instance}/api/v4/projects", headers=headers)
        for project in response.json():
            if project['path'] == project_name:
                return project['id']
        return None

    def get_project_name(self, url):
         # Regex pattern for SSH URL (supports group)
        ssh_pattern = r'git@github\.com[:/](.+?/.+?)(\.git)?$'
        # Regex pattern for HTTPS URL (supports group)
        https_pattern = r'https://github\.com/(.+?/.+?)(\.git)?$'
        
        # Check for SSH URL
        match_ssh = re.search(ssh_pattern, url)
        if match_ssh:
            return match_ssh.group(1)  # Repository name with group from SSH URL
        
        # Check for HTTPS URL
        match_https = re.search(https_pattern, url)
        if match_https:
            return match_https.group(1)  # Repository name with group from HTTPS URL

        return None 

    def get_mr_info(self, project_id, branch_name):
        url = f"https://{self.instance}/api/v4/projects/{project_id}/merge_requests?source_branch={branch_name}"
        headers = {"PRIVATE-TOKEN": self.token}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            mrs = response.json()
            if mrs:
                return {
                    "author": mrs[0]["author"]["name"],
                    "iid": mrs[0]["iid"],
                    "created_at": mrs[0]["created_at"]
                }
        else:
            self.logger.error(f"Error fetching MRs: {response.status_code} - {response.text}")
        return None

    def get_mr_description(self, project_id, iid):
        url = f"https://{self.instance}/api/v4/projects/{project_id}/merge_requests/{iid}"
        headers = {"PRIVATE-TOKEN": self.token}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            description = response.json().get("description")
            return description if description is not None else ""
        else:
            self.logger.error(f"Error fetching MR description: {response.status_code} - {response.text}")
            return ""
