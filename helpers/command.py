import subprocess
import os
from helpers.config import Config
from helpers.template import Template

class Command:
    
    @classmethod
    def compose_steward(cls):
        config = Config()
        dict_ = config.get_dict()
        #config.get_configuration_settings()
        Template.render(config)
        config.generate_ssl_certificate()
        # print(dict_)
        command = [
            'docker-compose',
            '-f',
            'docker-compose.db.yml',
            '-f',
            'docker-compose.backend.yml',
            '-f',
            'docker-compose.frontend.yml',
            'up',
            '-d'
        ]  
        subprocess.call(command, cwd= config.get_env_files_path())
    

    @classmethod
    def compose_particpant(cls):
        pass

    @classmethod
    def update(cls):
        pass