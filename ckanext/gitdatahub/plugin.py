import json
import logging
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanapi.datapackage import dataset_to_datapackage
from github import Github

log = logging.getLogger(__name__)

class GitDataHubException(Exception):
    pass


class GitdatahubPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController, inherit=True)

    # IConfigurer
    def configure(self, config):
        # TODO: Properly check and manage token
        if not config['ckanext.gitdatahub.access_token']:
            msg = 'ckanext.gitdatahub.access_token is missing from config file'
            raise GitDataHubException(msg)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'gitdatahub')

    def after_create(self, context, pkg_dict):
        token = toolkit.config.get('ckanext.gitdatahub.access_token')
        try:
            g = Github(token)
            repo = g.get_repo('pdelboca/gitdatahub-package')
            body = dataset_to_datapackage(pkg_dict)
            repo.create_file(
                'datapackage.json',
                'Create datapackage.json',
                json.dumps(body, indent=2)
                )
        except Exception as e:
            log.exception('Cannot create datapackage.json file.')

    #TODO: When updating after the creation resources are added, but not when
    # updating an already created package.
    def after_update(self, context, pkg_dict):
        token = toolkit.config.get('ckanext.gitdatahub.access_token')
        try:
            g = Github(token)
            repo = g.get_repo('pdelboca/gitdatahub-package')
            contents = repo.get_contents("datapackage.json")
            body = dataset_to_datapackage(pkg_dict)
            repo.update_file(
                contents.path,
                "Update datapackage.json",
                json.dumps(body, indent=2),
                contents.sha
                )
        except Exception as e:
            log.exception('Cannot update datapackage.json file.')

    def delete(self, entity):
        token = toolkit.config.get('ckanext.gitdatahub.access_token')
        try:
            g = Github(token)
            repo = g.get_repo("pdelboca/gitdatahub-package")
            contents = repo.get_contents("datapackage.json")
            repo.delete_file(
                    contents.path,
                    "Delete datapackage.json",
                    contents.sha
                    )
            log.info("datapackage.json file deleted.")
        except Exception as e:
            log.exception("Error when deleting datapackage.json file.")
