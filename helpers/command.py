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
        config.generate_ssl_certificate()
        Template.render(config)
        # print(dict_)
        exec_dir = os.path.join(dict_['base_dir'], 'docker')
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
        subprocess.call(command, cwd= exec_dir)
    

    @classmethod
    def compose_particpant(cls):
        pass

    @classmethod
    def update(cls):
        pass