import helpers
import logging

from ckan.lib.base import h, BaseController, render, abort, request
from ckan import model
from ckan.common import c
from ckan.logic import check_access, get_action, clean_dict, tuplize_dict, ValidationError, parse_params
from ckan.lib.navl.dictization_functions import unflatten


log = logging.getLogger(__name__)


class CommentController(BaseController):
    def add(self, dataset_id, content_type='dataset'):
        return self._add_or_reply('new', dataset_id, content_type)

    def edit(self, content_type, content_item_id, comment_id):

        context = {'model': model, 'user': c.user}
        data_dict = {'id': content_item_id}

        # Auth check to make sure the user can see this content item
        helpers.check_content_access(content_type, context, data_dict)

        try:
            # Load the content item
            helpers.get_content_item(content_type, context, data_dict)
        except:
            abort(403)

        if request.method == 'POST':
            data_dict = clean_dict(unflatten(
                tuplize_dict(parse_params(request.POST))))
            data_dict['id'] = comment_id
            data_dict['content_type'] = content_type
            data_dict['content_item_id'] = content_item_id
            success = False
            try:
                get_action('comment_update')(context, data_dict)
                success = True
            except ValidationError, ve:
                log.debug(ve)
                if ve.error_dict and ve.error_dict.get('message'):
                    msg = ve.error_dict['message']
                else:
                    msg = str(ve)
                h.flash_error(msg)
            except Exception, e:
                log.debug(e)
                abort(403)

            h.redirect_to(
                helpers.get_redirect_url(
                    content_type,
                    content_item_id if content_type == 'datarequest' else c.pkg.name,
                    'comment_' + str(comment_id) if success else 'edit_' + str(comment_id)
                ))

        return helpers.render_content_template(content_type)

    def reply(self, content_type, dataset_id, parent_id):
        c.action = 'reply'

        try:
            data = {'id': parent_id}
            c.parent_dict = get_action("comment_show")({'model': model, 'user': c.user},
                                                       data)
            c.parent = data['comment']
        except:
            abort(404)

        return self._add_or_reply('reply', dataset_id, content_type, parent_id)

    def _add_or_reply(self, comment_type, content_item_id, content_type, parent_id=None):
        """
       Allows the user to add a comment to an existing dataset
       """
        content_type = 'dataset' if 'content_type' not in vars() else content_type

        context = {'model': model, 'user': c.user}

        data_dict = {'id': content_item_id}

        # Auth check to make sure the user can see this content item
        helpers.check_content_access(content_type, context, data_dict)

        try:
            # Load the content item
            helpers.get_content_item(content_type, context, data_dict)
        except:
            abort(403)

        if request.method == 'POST':
            data_dict = clean_dict(unflatten(
                tuplize_dict(parse_params(request.POST))))
            data_dict['parent_id'] = c.parent.id if c.parent else None
            data_dict['url'] = '/%s/%s' % (content_type, content_item_id if content_type == 'datarequest' else c.pkg.name)
            success = False
            try:
                res = get_action('comment_create')(context, data_dict)
                success = True
            except ValidationError, ve:
                log.debug(ve)
                if ve.error_dict and ve.error_dict.get('message'):
                    msg = ve.error_dict['message']
                else:
                    msg = str(ve)
                h.flash_error(msg)
            except Exception, e:
                log.debug(e)
                abort(403)

            h.redirect_to(
                helpers.get_redirect_url(
                    content_type,
                    content_item_id if content_type == 'datarequest' else c.pkg.name,
                    'comment_' + str(res['id']) if success else ('comment_form' if comment_type == 'new' else 'reply_' + str(parent_id))
                ))

        return helpers.render_content_template(content_type)

    def delete(self, content_type, content_item_id, comment_id):

        context = {'model': model, 'user': c.user}

        data_dict = {'id': content_item_id}

        # Auth check to make sure the user can see this content item
        helpers.check_content_access(content_type, context, data_dict)

        try:
            # Load the content item
            helpers.get_content_item(content_type, context, data_dict)
        except:
            abort(403)

        try:
            data_dict = {'id': comment_id, 'content_type': content_type, 'content_item_id': content_item_id}
            get_action('comment_delete')(context, data_dict)
        except Exception, e:
            log.debug(e)
            if e.error_dict and e.error_dict.get('message'):
                msg = e.error_dict['message']
            else:
                msg = str(e)
            h.flash_error(msg)

        h.redirect_to(
            helpers.get_redirect_url(
                content_type,
                content_item_id if content_type == 'datarequest' else c.pkg.name,
                'comment_' + str(comment_id)
            ))

        return helpers.render_content_template(content_type)
