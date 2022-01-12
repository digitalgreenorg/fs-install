#!/usr/bin/env python3
'''
Steps to install Farmstack central.
1. Setup UserManagement with DB.
2. Setup GraphQL Central backend with DB.
3. Setup React + Nginx.
'''

import os
import subprocess
import json

from subprocess import CalledProcessError
from helpers.config import Config

import jinja2

host = ""

jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(Config.STEWARD_UI_DIR, 'config')))


def run_mysql_connector():
    os.chdir(os.path.join(Config.USER_MANAGEMENT_DIR, 'deploy'))
    command = ['docker-compose', 'up', '-d', 'mysql']
    subprocess.run(command, shell=True)
    os.chdir(Config.BASE_DIR)


def generate_ssl_certificate(host):
    try:
        ui_config_dir = os.path.join(Config.STEWARD_UI_DIR, 'config')
        lets_encrypt_dir = os.path.join(Config.LETS_ENCRYPT_BASE_URL, host)
        cert_files = {
            'public.crt': 'fullchain.pem',
            'private.key': 'privkey.pem'
        }
        print("Generating SSL Certificate...")

        # 1. Install certbot.
        subprocess.run("sudo apt-get install certbot", shell=True)

        # 2. Provide Information..
        email = input("Enter your email for TLS/SSL certificate renewal:")
        certbot_command = ['sudo', 'certbot', 'certonly', '--standalone', '-d', host, '--agree-tos',
                           '--non-interactive', '-m', email]
        subprocess.run(certbot_command, shell=True)

        # 3. Copy Keys to config folder and change permissions.
        for key in cert_files.keys():
            cert_file = os.path.join(ui_config_dir, key)
            lets_encrypt_file = os.path.join(lets_encrypt_dir, cert_files[key])
            subprocess.run(["sudo", "cp", lets_encrypt_file, cert_file], shell=True)
            subprocess.run(['sudo', 'chown', '${USER}:${USER}', cert_file], shell=True)

        print("Done with SSL Certificate...")
    except Exception as err:
        print("Error Installing SSL Certificate")
        return


def create_env_file():
    global host
    template = jinja_env.get_template('env_template.env')
    # subprocess.call("touch ~/fs-steward/config.env", shell=True)
    print("************************CONFIGURE ENVIRONMENT VARIABLES********************************************")
    db_user = input("Enter DB User: ")
    db_password = input("Enter User Password for DB: ")
    db_root_password = input("Enter Root Password: ")
    sendgrid_email = input("Enter email registered with sendgrid: ")
    sendgrid_key = input("Enter SendGrid Key: ")
    domain = input("Enter domain: ")
    google_client_id = input("Enter Google Client ID: ")
    # subprocess.call("chmod 660 ~/fs-steward/config.env", shell=True)
    input_config = {
        'db_user': db_user,
        'db_password': db_password,
        'db_root_password': db_root_password,
        'sendgrid_key': sendgrid_key,
        'sendgrid_email': sendgrid_email,
        'domain': domain,
        'google_client_id': google_client_id
    }
    print("****************************EVALUATE YOUR INPUT****************************************")
    print(template.render(input_config))
    print("*******************************END OF YOUR INPUT*************************************")

    choice = input("Is the above configuration Ok(yes/no)")
    if choice == "yes" or choice == "Yes" or choice == "y":
        try:
            host = domain
            # print(os.getcwd())
            config_file = open("config.env", 'w')
            config_file.write(template.render(input_config))
            config_file.close()
        except Exception as e:
            print("Some issue with writing environmental configuration file", e)

    elif choice == "no" or choice == "No" or choice == "n":
        create_env_file()
    else:
        print("Some issue with creating environment variables...")
        return

    try:
        db_config = open("node-config.json", "w")
        db_config.write(
            json.dumps({
                "UserManagement": {
                    "dbConfig": {
                        "HOST": "mysql",
                        "USER": db_user,
                        "PASSWORD": db_password,
                        "DB": "usermanagement",
                        "dialect": "mysql",
                        "pool": {
                            "max": 5,
                            "min": 0,
                            "acquire": 30000,
                            "idle": 10000
                        }
                    }
                }
            })
        )
    except Exception as err:
        print("Failed to write configuration to JSON file", err)
        return


def push_env_file():
    env_files = {
        '%s/.env.production' % Config.STEWARD_UI_DIR: 'config.env',
        '%s/config/default.json' % Config.USER_MANAGEMENT_DIR: 'node-config.json',
        '%s/.env' % Config.USER_MANAGEMENT_DIR: 'config.env',
        '%s/deploy/.env' % Config.USER_MANAGEMENT_DIR: 'config.env',
        '%s/FS_central_api/.env' % Config.STEWARD_API_DIR: 'config.env',
    }
    for key in env_files.keys():
        command = ['cp', key, env_files[key]]
        subprocess.run(command, shell=True)

    # subprocess.run('cp config.env %s/.env.production' % (Config.STEWARD_UI_DIR), shell=True)
    # subprocess.run('cp node-config.json %s/config/default.json' % (Config.USER_MANAGEMENT_DIR), shell=True)
    # subprocess.run('cp config.env %s/.env' % (Config.USER_MANAGEMENT_DIR), shell=True)
    # subprocess.run('cp config.env %s/deploy/.env' % (Config.USER_MANAGEMENT_DIR), shell=True)
    # subprocess.run('cp config.env %s/FS_central_api/.env' % (Config.STEWARD_API_DIR), shell=True)


def configure_nginx(host):
    template = jinja_env.get_template('template.conf')
    if len(host) == 0:
        print("No host provided..")
        exit()

    var = {
        'host': host
    }
    # print(template.render(var))
    os.chdir(Config.BASE_DIR)

    try:
        config_file = open(Config.STEWARD_UI_DIR + "/config/nginx.conf", 'w')
        config_file.write(template.render(var))
        config_file.close()
    except Exception as e:
        print("Some issue with writing nginx configuration to file", e)


def configure_steward_usm(host):
    pass


def configure_steward_graphql(host):
    pass


def configure():
    # Configure Nginx
    global host
    generate_ssl_certificate(host)
    configure_nginx(host)
    configure_steward_usm(host)
    configure_steward_graphql(host)


def run_docker_containers():
    os.chdir(Config.USER_MANAGEMENT_DIR + "/deploy")
    containers = ['usm', 'fs-central-api', 'steward-ui']
    for container in containers:
        subprocess.call("docker-compose up -d %s" % (container), shell=True)
    # subprocess.call("docker run -p 80:80 -p 443:443 farmstack/steward-ui:test", shell=True)


def build_docker_images(repo_dir, image_tag):
    command = ['docker', 'build', '-t', image_tag, repo_dir]
    subprocess.call(command, shell=True)


def clone_repositories(repo_dir, branch):
    if os.path.isdir(repo_dir):
        print('repository "%s" already exist' % repo_dir)
        return

    try:
        command = ["git", "clone", Config.GIT_BASE_URL+repo_dir+'.git']
        process = subprocess.run(command, shell=True, check=True)
        os.chdir(repo_dir)
        command = ['git', 'checkout', branch]
        subprocess.call(command, shell=True)
        os.chdir(Config.BASE_DIR)

    except CalledProcessError as err:
        print("Problem fetching repositories... Kindly check with Permissions")


def start_setup():
    try:
        python_command = "python3 -V"
        process = subprocess.run(python_command, shell=True)

    except CalledProcessError as err:
        print(err.output)
        return
    for idx, repository in enumerate(Config.REPOSITORIES_URLS):
        clone_repositories(repository, Config.REPOSITORIES_BRANCHES[idx])
        build_docker_images(repository, Config.DOCKER_IMAGES[idx])

    os.chdir(Config.BASE_DIR)

    create_env_file()
    push_env_file()
    run_mysql_connector()
    configure()
    run_docker_containers()


if __name__ == "__main__":
    start_setup()
