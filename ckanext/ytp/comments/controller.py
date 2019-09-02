import ckan.plugins.toolkit as toolkit
import email_notifications
import helpers
import logging
import notification_helpers

from ckan.lib.base import h, BaseController, render, abort, request
from ckan import model
from ckan.common import c
from ckan.logic import check_access, get_action, clean_dict, tuplize_dict, ValidationError, parse_params
from ckan.lib.navl.dictization_functions import unflatten


log = logging.getLogger(__name__)


class CommentController(BaseController):
    def add(self, dataset_id):
        return self._add_or_reply('new', dataset_id)

    def edit(self, dataset_id, comment_id):

        context = {'model': model, 'user': c.user}

        # Auth check to make sure the user can see this package

        data_dict = {'id': dataset_id}
        check_access('package_show', context, data_dict)

        try:
            c.pkg_dict = get_action('package_show')(context, {'id': dataset_id})
            c.pkg = context['package']
        except:
            abort(403)

        if request.method == 'POST':
            data_dict = clean_dict(unflatten(
                tuplize_dict(parse_params(request.POST))))
            data_dict['id'] = comment_id
            success = False
            try:
                res = get_action('comment_update')(context, data_dict)
                success = True
            except ValidationError, ve:
                log.debug(ve)
            except Exception, e:
                log.debug(e)
                abort(403)

            if success:
                h.redirect_to(str('/dataset/%s#comment_%s' % (c.pkg.name, res['id'])))

        return render("package/read.html")

    def reply(self, dataset_id, parent_id):
        c.action = 'reply'

        try:
            data = {'id': parent_id}
            c.parent_dict = get_action("comment_show")({'model': model, 'user': c.user},
                                                       data)
            c.parent = data['comment']
        except:
            abort(404)

        return self._add_or_reply('reply', dataset_id)

    def _add_or_reply(self, comment_type, dataset_id):
        """
       Allows the user to add a comment to an existing dataset
       """
        content_type = 'dataset'

        context = {'model': model, 'user': c.user}

        # Auth check to make sure the user can see this package

        data_dict = {'id': dataset_id}
        check_access('package_show', context, data_dict)

        try:
            c.pkg_dict = get_action('package_show')(context, {'id': dataset_id})
            c.pkg = context['package']
        except:
            abort(403)

        if request.method == 'POST':
            data_dict = clean_dict(unflatten(
                tuplize_dict(parse_params(request.POST))))
            data_dict['parent_id'] = c.parent.id if c.parent else None
            data_dict['url'] = '/dataset/%s' % c.pkg.name
            success = False
            try:
                res = get_action('comment_create')(context, data_dict)
                success = True
            except ValidationError, ve:
                log.debug(ve)
            except Exception, e:
                log.debug(e)
                abort(403)

            if success:
                email_notifications.notify_admins_and_comment_notification_recipients(
                    helpers.get_org_id(content_type),
                    toolkit.c.userobj,
                    'notification-new-comment',
                    content_type,
                    helpers.get_content_item_id(content_type),
                    res['thread_id'],
                    res['parent_id'] if comment_type == 'reply' else None,
                    res['id']
                )

                if notification_helpers.comment_notification_recipients_enabled():
                    if comment_type == 'reply':
                        # Add the user who submitted the reply to comment notifications for this thread
                        notification_helpers.add_commenter_to_comment_notifications(toolkit.c.userobj.id, res['thread_id'], res['parent_id'])
                    else:
                        # Add the user who submitted the comment notifications for this new thread
                        notification_helpers.add_commenter_to_comment_notifications(toolkit.c.userobj.id, res['thread_id'], res['id'])

                h.redirect_to(str('/dataset/%s#comment_%s' % (c.pkg.name, res['id'])))

        return render("package/read.html")

    def delete(self, dataset_id, comment_id):

        context = {'model': model, 'user': c.user}

        # Auth check to make sure the user can see this package

        data_dict = {'id': dataset_id}
        check_access('package_show', context, data_dict)

        try:
            c.pkg_dict = get_action('package_show')(context, {'id': dataset_id})
            c.pkg = context['package']
        except:
            abort(403)

        try:
            data_dict = {'id': comment_id}
            get_action('comment_delete')(context, data_dict)
        except Exception, e:
            log.debug(e)

        h.redirect_to(str('/dataset/%s' % c.pkg.name))

        return render("package/read.html")
