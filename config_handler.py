import json
import logging

class ConfigHandler:
    def __init__(self, config_name):
        self.config_name = config_name
        self.logger = logging.getLogger(__name__)

    def load_config(self):
        try:
            with open(self.config_name, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            self.logger.info(f"Configuration file '{self.config_name}' not found. Creating a new one.")
            return self.create_config()

    def create_config(self):
        try:
            instance = input("Enter GitLab instance > ")
            token = input("Enter GitLab token > ")
            data = {
                "instance": instance,
                "token": token,
            }
            with open(self.config_name, 'w') as config:
                json.dump(data, config)
            self.logger.info(f"Configuration file '{self.config_name}' created successfully.")
            return data
        except Exception as e:
            self.logger.error(f"Error creating configuration file: {e}")
            return None