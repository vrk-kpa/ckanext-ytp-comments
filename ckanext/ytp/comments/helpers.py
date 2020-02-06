import ckan.plugins.toolkit as toolkit
import logging

from ckan.common import c

log = logging.getLogger(__name__)


def get_org_id(content_type):
    return c.datarequest['organization_id'] if content_type == 'datarequest' else c.pkg.owner_org


def get_content_item_id(content_type):
    return c.datarequest['id'] if content_type == 'datarequest' else c.pkg.name


def get_user_id():
    user = toolkit.c.userobj
    return user.id
