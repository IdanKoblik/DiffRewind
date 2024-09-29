import json
import logging
from pathlib import Path
from typing import Dict, Optional

class ConfigHandler:
    def __init__(self, config_name: str):
        self.config_name = Path(config_name)
        self.logger = logging.getLogger(__name__)

    def load_config(self) -> Optional[Dict[str, str]]:
        try:
            with self.config_name.open('r') as file:
                return json.load(file)
        except FileNotFoundError:
            self.logger.info(f"Configuration file '{self.config_name}' not found. Creating a new one.")
            return self.create_config()

    def create_config(self) -> Optional[Dict[str, str]]:
        try:
            instance = input("Enter GitLab instance > ")
            token = input("Enter GitLab token > ")
            data = {
                "instance": instance,
                "token": token,
            }
            with self.config_name.open('w') as config:
                json.dump(data, config, indent=2)
            self.logger.info(f"Configuration file '{self.config_name}' created successfully.")
            return data
        except Exception as e:
            self.logger.error(f"Error creating configuration file: {e}")
            return None