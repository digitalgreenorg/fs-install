import sys
import os
import fnmatch
from string import Template as PyTemplate
from helpers.cli import CLI

class Template:

    @classmethod
    def render(cls, config):
        dict_ = config.get_dict()
        template_variables = cls.__get_template_variables(config)
        templates_path_parent = config.get_env_files_path()
        environment_path_parent = os.path.realpath(os.path.normpath(os.path.join(
            dict_['base_dir'],
            'docker')))
        # Environment variables for all services.
        cls.__write_templates(template_variables, templates_path_parent, environment_path_parent)
        # Database default config for usm.
        cls.__write_templates_db_config(template_variables, os.path.join(dict_['base_dir'], 'templates', 'usm-db-config'), environment_path_parent)
        # Nginx config
        cls.__write_templates_nginx_config(template_variables, os.path.join(dict_['base_dir'], 'templates', 'nginx'), environment_path_parent)

    @staticmethod
    def __write_templates_db_config(template_variables_, template_root_, env_root_):

        with open(os.path.join(template_root_, 'default-db-config.json.tpl'), 'r') as template:
            t = ExtendedPyTemplate(template.read(), template_variables_)
            template.close()
            
        with open(os.path.join(env_root_, 'config', 'default.json'),'w') as f:
            f.write(t.substitute(template_variables_))
            f.close()
    
    @staticmethod
    def __write_templates_nginx_config(template_variables_, template_root_, env_root_):

        with open(os.path.join(template_root_, 'template.conf.tpl'), 'r') as template:
            t = ExtendedPyTemplate(template.read(), template_variables_)
            template.close()
            
        with open(os.path.join(env_root_, 'config', 'nginx.conf'),'w') as f:
            f.write(t.substitute(template_variables_))
            f.close()

    @staticmethod
    def __write_templates(template_variables_, template_root_, env_root_):
        
        with open(os.path.join(template_root_, 'env.txt.tpl'), 'r') as template:
            t = ExtendedPyTemplate(template.read(), template_variables_)
            template.close()
            
        with open(os.path.join(env_root_, '.env'),'w') as f:
            f.write(t.substitute(template_variables_))
            f.close()
        

    
    @staticmethod
    def __get_template_variables(config):
        dict_ = config.get_dict()
        try:
            return {
            # Front end
            'REACT_APP_BASE_URL' : dict_['usm_service'],
            'REACT_APP_API_BASE_URL':dict_['graphql_service'],
            'REACT_APP_GOOGLE_CLIENT_ID': dict_['google_oauth_client_id'],
            'PUBLIC_DOMAIN': dict_['public_domain'],
            'REACT_APP_CONNECTOR_HOSTING': dict_['graphql_service'],
            'REACT_APP_CONNECTOR_HOST_IP' : dict_['host_ip'],
            'STEWARD_URL': dict_['steward_url'],
            #UserManagement
            'PORT' : dict_['usm_service_port'],
            'SENDGRID_KEY' : dict_['sendgrid_key'],
            'SENDER_EMAIL_ID' : dict_['sendgrid_registered_email'],
            'BASE_URL' : dict_['invitation_url'],
            'JWT_EXP_TIME' : dict_['jwt_expiration_time'],
            'EMAIL_VERIFICATION_TIME' : dict_['email_verification_time'],
            'VERIFICATION_EMAIL_URL' : dict_['verification_email_url'],
            'SET_PASSWORD_URL_FRONTEND' : dict_['frontend_setpassword_url'],
            'IMG_MAX_SIZE' : dict_['image_max_size'],
            'FILE_MAX_SIZE' : dict_['file_max_size'],

            # Steward-API
            'SECRET_KEY' : dict_['steward_graphql_secret_key'],
            'DB_ENGINE': dict_['steward_db_engine'],

            #Database
            'DB_NAME' : dict_['steward_db_name'],
            'DB_USER' : dict_['steward_db_user'],
            'DB_PASSWORD' : dict_['steward_db_user_password'],
            'DB_HOST' : dict_['steward_db_host'],
            'DB_ROOT_PASSWORD' : dict_['steward_root_password'],
            'request_uri' : '$request_uri',
            'uri' : '$uri',
            'FS_STEWARD_UI_VERSION': '1.0.0',
            'FS_STEWARD_API_VERSION': '1.0.0',
            'FS_USM_VERSION' : '1.0.0'
            }
        except Exception as err:
            CLI.colored_print('Issue with Configuration file.', CLI.COLOR_ERROR)
            sys.exit(1)

class ExtendedPyTemplate(PyTemplate):
    """
    Basic class to add conditional substitution to `string.Template`

    """
    IF_PATTERN = '{{% if {} %}}'
    ENDIF_PATTERN = '{{% endif {} %}}'

    def __init__(self, template, template_variables_):
        for key, value in template_variables_.items():
            if self.IF_PATTERN.format(key) in template:
                if value:
                    if_pattern = r'{}\s*'.format(self.IF_PATTERN.format(key))
                    endif_pattern = r'\s*{}'.format(
                        self.ENDIF_PATTERN.format(key))
                    template = re.sub(if_pattern, '', template)
                    template = re.sub(endif_pattern, '', template)
                else:
                    pattern = r'{}(.|\s)*?{}'.format(
                        self.IF_PATTERN.format(key),
                        self.ENDIF_PATTERN.format(key))
                    template = re.sub(pattern, '', template)
        super(ExtendedPyTemplate, self).__init__(template)