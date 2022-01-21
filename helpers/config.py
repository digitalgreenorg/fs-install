
import os
import time
import json
import stat
from cli import CLI

class Config:

    GIT_BASE_URL = 'git@github.com:digitalgreenorg'

    STEWARD_API_REPO = 'FS-Central-API'
    STEWARD_API_BRANCH = 'central_v2'

    STEWARD_UI_REPO = 'FS-Central-UI'
    STEWARD_UI_BRANCH = 'mayank/new/dockerise'

    USER_MANAGEMENT_REPO = 'UserManagement-BE'
    USER_MANAGEMENT_BRANCH = 'dataset-user'

    BASE_DIR = os.environ['PWD']
    DEPLOY_DIR = os.path.join(BASE_DIR, '.deploy')
    USER_MANAGEMENT_DIR = os.path.join(DEPLOY_DIR, USER_MANAGEMENT_REPO)
    STEWARD_UI_DIR = os.path.join(DEPLOY_DIR, STEWARD_UI_REPO)
    STEWARD_API_DIR = os.path.join(DEPLOY_DIR, STEWARD_API_REPO)

    REPOSITORIES_URLS = [STEWARD_API_REPO, STEWARD_UI_REPO, USER_MANAGEMENT_REPO]
    REPOSITORIES_BRANCHES = [STEWARD_API_BRANCH, STEWARD_UI_BRANCH, USER_MANAGEMENT_BRANCH]

    STEWARD_UI_DOCKER_IMAGE = 'farmstack/steward-ui:test'
    STEWARD_API_DOCKER_IMAGE = 'farmstack/steward-graphql:test'
    USER_MANAGEMENT_DOCKER_IMAGE = 'farmstack/steward-user-management:test'

    DOCKER_IMAGES = [STEWARD_API_DOCKER_IMAGE, STEWARD_UI_DOCKER_IMAGE, USER_MANAGEMENT_DOCKER_IMAGE]

    LETS_ENCRYPT_BASE_URL = '/etc/letsencrypt/live/'

    CONFIG_FILE = '.run.conf'

    def __init__(self):
        self.first_time = None
        self.__dict = self.read_config()
    
    def read_config(self):
        dict_ = {}
        try:
            base_dir = os.path.dirname(
                os.path.dirname(os.path.realpath(__file__)))
            config_file = os.path.join(base_dir, Config.CONFIG_FILE)
            with open(config_file, 'r') as f:
                dict_ = dict()
        except IOError:
            CLI.colored_print(message='Configuration File does not exist!', color=CLI.COLOR_WARNING)
        return dict_
    
    def write_config(self):

        if self.__dict.get('date_created') is None:
            self.__dict['date_created'] = int(time.time())
        self.__dict['date_modified'] = int(time.time())

        try:
            base_dir = os.path.dirname(
                os.path.dirname(os.path.realpath(__file__)))
            config_file = os.path.join(base_dir, Config.CONFIG_FILE)
            with open(config_file, 'w') as f:
                f.write(json.dumps(self.__dict, indent=2, sort_keys=True))

            os.chmod(config_file, stat.S_IWRITE | stat.S_IREAD)

        except IOError:
            CLI.colored_print('Could not write configuration file',
                              CLI.COLOR_ERROR)
            sys.exit(1)

config = Config()
config.write_config()






