#!/usr/bin/sudo
import os
import time
import json
import sys
import stat
import subprocess
import tempfile
from helpers.cli import CLI
from helpers.template import Template
from version import __version__

class Config:

    GIT_BASE_URL = 'https://github.com/digitalgreenorg/fs-install.git'

    INSTALL_GIT_URL = 'https://github.com/digitalgreenorg/fs-install.git'

    STEWARD_API_REPO = 'FS-Central-API'
    STEWARD_API_BRANCH = 'central_v2'

    STEWARD_UI_REPO = 'FS-Central-UI'
    STEWARD_UI_BRANCH = 'mayank/new/dockerise'

    USER_MANAGEMENT_REPO = 'UserManagement-BE'
    USER_MANAGEMENT_BRANCH = 'dataset-user'

    # BASE_DIR = os.environ['PWD']
    # DEPLOY_DIR = os.path.join(BASE_DIR, '.deploy')
    # USER_MANAGEMENT_DIR = os.path.join(DEPLOY_DIR, USER_MANAGEMENT_REPO)
    # STEWARD_UI_DIR = os.path.join(DEPLOY_DIR, STEWARD_UI_REPO)
    # STEWARD_API_DIR = os.path.join(DEPLOY_DIR, STEWARD_API_REPO)

    # REPOSITORIES_URLS = [STEWARD_API_REPO, STEWARD_UI_REPO, USER_MANAGEMENT_REPO]
    # REPOSITORIES_BRANCHES = [STEWARD_API_BRANCH, STEWARD_UI_BRANCH, USER_MANAGEMENT_BRANCH]

    STEWARD_UI_DOCKER_IMAGE = 'farmstack/steward-ui:test'
    STEWARD_API_DOCKER_IMAGE = 'farmstack/steward-graphql:test'
    USER_MANAGEMENT_DOCKER_IMAGE = 'farmstack/steward-user-management:test'

    DOCKER_IMAGES = [STEWARD_API_DOCKER_IMAGE, STEWARD_UI_DOCKER_IMAGE, USER_MANAGEMENT_DOCKER_IMAGE]

    LETS_ENCRYPT_BASE_URL = '/etc/letsencrypt/live/'

    CONFIG_FILE = '.run.conf'
    STEWARD_INSTALL_VERSION = __version__
    ENV_FILES_DIR = 'envfiles'

    RELEASE_URL = 'https://gist.githubusercontent.com/mgautam099/754cfeefaaf061469be75ebf740f5df4/raw/62023fc414cf11d5f91c435605f9ac985e586812/releases.json'

    def __init__(self):
        self.__dict = self.read_config()

    def discard_config(self):
        try:
            base_dir = os.path.dirname(
                os.path.dirname(os.path.realpath(__file__)))
            config_file = os.path.join(base_dir, Config.CONFIG_FILE)
            command = f"rm {CONFIG_FILE}"
            CLI.run_command(command, cwd=self.base_dir)
            self.__dict = None
        except IOError:
            CLI.colored_print("Could not remove the configuration file", color=CLI.COLOR_ERROR)
            sys.exit(1)
    
    def read_config(self):
        dict_ = {}
        try:
            base_dir = os.path.dirname(
                os.path.dirname(os.path.realpath(__file__)))
            config_file = os.path.join(base_dir, Config.CONFIG_FILE)
            with open(config_file, 'r') as f:
                dict_ = json.loads(f.read())
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

        except IOError as err:
            CLI.colored_print(err,
                              CLI.COLOR_ERROR)
            sys.exit(1)

    def get_dict(self):
        return self.__dict
     
    def __welcome(self):
        message = (
            'Welcome to Farmstack.\n'
            '\n'
            'You are going to be asked some questions that will install '
            'Farmstack on your system.\n'
            '\n'
            'Some questions already have default values (within brackets).\n'
            'Otherwise type your answer. '
        )
        CLI.framed_print(message, color=CLI.COLOR_INFO)
        self.__dict['base_dir'] = os.path.dirname(
                os.path.dirname(os.path.realpath(__file__)))

    def __update_hosts(cls):
        """

        Args:
            dict_ (dict): Dictionary provided by `Config.get_dict()`
        """
        dict_ = cls.__dict
        if dict_['local_installation']:
            start_sentence = '### (BEGIN) Farmstack local routes'
            end_sentence = '### (END) Farmstack local routes'

            _, tmp_file_path = tempfile.mkstemp()

            with open('/etc/hosts', 'r') as f:
                tmp_host = f.read()

            start_position = tmp_host.find(start_sentence)
            end_position = tmp_host.find(end_sentence)

            if start_position > -1:
                tmp_host = tmp_host[0: start_position] \
                           + tmp_host[end_position + len(end_sentence) + 1:]

            routes = '{ip_address}  ' \
                     '{public_domain_name} ' .format(
                        ip_address='127.0.0.1',
                        public_domain_name=dict_['public_domain'],
                     )

            tmp_host = ('{bof}'
                        '\n{start_sentence}'
                        '\n{routes}'
                        '\n{end_sentence}'
                        ).format(
                bof=tmp_host.strip(),
                start_sentence=start_sentence,
                routes=routes,
                end_sentence=end_sentence
            )

            print(tmp_host)

            with open(tmp_file_path, 'w') as f:
                f.write(tmp_host)
                f.close()

            message = (
                'Privileges escalation is required to update '
                'your `/etc/hosts`.'
            )
            CLI.framed_print(message, color=CLI.COLOR_INFO)
            config = Config()
            config.write_config()

            cmd = (
                'sudo cp /etc/hosts /etc/hosts.old '
                '&& sudo cp {tmp_file_path} /etc/hosts'
            ).format(tmp_file_path=tmp_file_path)

            return_value = os.system(cmd)

            os.unlink(tmp_file_path)

            if return_value != 0:
                CLI.colored_print("Some issue with writing to Host file", color=CLI.COLOR_ERROR)
                sys.exit(1)


    def __questions_steward_frontend(self):

        CLI.framed_print(message=('Step 1:'
            ' Configuring Steward Frontend'))
        self.__dict['host_ip'] = CLI.colored_input(message='Enter public IP of the instance:')
        self.__dict['public_domain'] = CLI.colored_input(message='Enter domain registered for this instance: ')
        if self.__dict['protocol'] == 'http':
            self.__dict['is_secured'] = False
            self.__dict['local_installation'] = True
            self.__update_hosts()
            # self.__modify_local_host(self.__dict['public_domain'])
        self.__dict['usm_service'] = f"{self.__dict['protocol']}://{self.__dict['public_domain']}/be"
        self.__dict['graphql_service'] = f"{self.__dict['protocol']}://{self.__dict['public_domain']}/cbe"
        self.__dict['google_oauth_client_id'] = CLI.colored_input(message='Enter Google Client ID: ')

    def get_env_files_path(self):
        current_path = os.path.realpath(os.path.normpath(os.path.join(
            self.__dict['base_dir'],
            'templates',
            self.ENV_FILES_DIR
        )))
        return current_path
    
    
    def generate_ssl_certificate(self):

        try:
            lets_encrypt_dir = os.path.join(Config.LETS_ENCRYPT_BASE_URL, self.__dict['public_domain'])
            cert_files = {
                'public.crt': 'fullchain.pem',
                'private.key': 'privkey.pem'
            }

            # 1. Install certbot.
            subprocess.run("sudo apt-get install certbot", shell=True)

            # 2. Provide Information..
            email = CLI.colored_input(message='Enter your email for TLS/SSL certificate renewal: ')
            if(self.__dict['is_secured']):
                certbot_command = ['sudo', 'certbot', 'certonly', '--standalone', '-d', self.__dict['public_domain'], '--agree-tos',
                            '--non-interactive', '-m', email]
            else:
                certbot_command = f"sudo openssl req -x509 -nodes -newkey rsa:1024 -days 1 -keyout /etc/letsencrypt/live/{self.__dict['public_domain']}/privkey.pem -out /etc/letsencrypt/live/{self.__dict['public_domain']}/fullchain.pem -subj /CN=localhost"
            # print(certbot_command)
            CLI.run_command(certbot_command)

            # 3. Copy Keys to config folder and change permissions.
            for key in cert_files.keys():
                cert_file = os.path.join(self.__dict['base_dir'], 'docker', 'nginx-cert', key)
                lets_encrypt_file = os.path.join(lets_encrypt_dir, cert_files[key])
                # print(cert_file, lets_encrypt_file)
                command = f"sudo cp {lets_encrypt_file} {cert_file}"
                # print(command)
                CLI.run_command(command)
                change_owner_command = f"sudo chown waseem {cert_file}"
                CLI.run_command(change_owner_command)

        except Exception as err:
            CLI.colored_print(message=err, color=CLI.COLOR_ERROR)
            sys.exit(1)
    
    def __questions_steward_backend_usm(self):
        CLI.framed_print(message=('Step 2:'
            'Configuring Steward UserManagement Service'))
        self.__dict['sendgrid_key'] = CLI.colored_input(message='Enter your sendgrid key: ')
        self.__dict['sendgrid_registered_email'] = CLI.colored_input(message='Enter registered e-mail with sendgrid: ')
        self.__dict['email_verification_time'] = '1h'
        self.__dict['jwt_expiration_time'] = '24h'
        self.__dict['verification_email_url'] = f"{self.__dict['usm_service']}/api/v1/verifyemail"
        self.__dict['frontend_setpassword_url'] = f"{self.__dict['protocol']}://{self.__dict['public_domain']}/set-password"
        self.__dict['usm_service_port'] = CLI.colored_input(message='Enter the port for user-management service: ')
        self.__dict['invitation_url'] = f"{self.__dict['protocol']}://{self.__dict['public_domain']}/login"
        self.__dict['image_max_size'] = 2
        self.__dict['file_max_size'] = 10

    def __questions_steward_backend_graphql(self):
        CLI.framed_print(message=('Step 3:'
            ' Configuring Steward API Service'))
        self.__dict['steward_graphql_secret_key'] = CLI.colored_input(message='Enter a secret key: ')
        self.__dict['steward_db_engine'] = 'django.db.backends.mysql'

    def __questions_steward_database(self):
        CLI.framed_print(message=('Step 3:'
            ' Configuring Database'))
        self.__dict['steward_db_name'] = 'usermanagement'
        self.__dict['steward_db_host'] = 'mysql'
        self.__dict['steward_db_user'] = CLI.colored_input(message='Enter database user: ')
        self.__dict['steward_db_user_password'] = CLI.colored_input(message='Enter password: ')
        self.__dict['steward_root_password'] = CLI.colored_input(message='Enter root password :')

    def __install_where(self):
        CLI.framed_print(message=('HTTP - For quick overview or insecure.\n'
                                'HTTPS - Secured.'))
        self.__dict['protocol'] = 'http' if CLI.yes_no_question(question="Do you want to setup HTTP or HTTPS?", labels=['http','https']) else 'https'
        

    def get_configuration_settings(self):
        self.__welcome()
        self.__install_where()
        self.__questions_steward_frontend()
        self.__questions_steward_backend_usm()
        self.__questions_steward_backend_graphql()
        self.__questions_steward_database()
        self.write_config()
        
    
