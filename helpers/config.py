
import os


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

