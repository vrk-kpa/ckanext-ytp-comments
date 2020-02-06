import ckan.plugins.toolkit as toolkit

from ckan.common import c, config
from ckan.lib.base import render
from ckan.logic import check_access, get_action
from ckanext.datarequests import actions


def get_content_item(content_type, context, data_dict):
    if content_type == 'datarequest':
        c.datarequest = actions.show_datarequest(context, data_dict)
    else:
        data_dict['include_tracking'] = True
        c.pkg_dict = get_action('package_show')(context, data_dict)
        c.pkg = context['package']


def check_content_access(content_type, context, data_dict):
    check_access('show_datarequest' if content_type == 'datarequest' else 'package_show', context, data_dict)


def get_redirect_url(content_type, content_item_id, anchor):
    return '/%s/%s#%s' % (
        'datarequest/comment' if content_type == 'datarequest' else 'dataset',
        content_item_id,
        anchor
    )


def render_content_template(content_type):
    return render(
        'datarequests/comment.html' if content_type == 'datarequest' else "package/read.html"
    )


def get_org_id(content_type):
    return c.datarequest['organization_id'] if content_type == 'datarequest' else c.pkg.owner_org


def ytp_comments_enabled():
    return "ytp_comments" in config.get('ckan.plugins', False)


def get_datarequest_comments_badge(datarequest_id):
    return toolkit.render_snippet('datarequests/snippets/badge.html',
                                  {'comments_count': toolkit.h.get_comment_count_for_dataset(datarequest_id,
                                                                                             'datarequest')})
