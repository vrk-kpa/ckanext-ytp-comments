import logging

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
                if ve.error_dict and ve.error_dict.get('message'):
                    msg = ve.error_dict['message']
                else:
                    msg = str(ve)
                h.flash_error(msg)
            except Exception, e:
                log.debug(e)
                abort(403)

            h.redirect_to(str('/dataset/%s#edit_%s' % (c.pkg.name, res['id'] if success else comment_id)))

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

        return self._add_or_reply('reply', dataset_id, parent_id)

    def _add_or_reply(self, comment_type, dataset_id, parent_id=None):
        """
       Allows the user to add a comment to an existing dataset
       """
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
                if ve.error_dict and ve.error_dict.get('message'):
                    msg = ve.error_dict['message']
                else:
                    msg = str(ve)
                h.flash_error(msg)
            except Exception, e:
                log.debug(e)
                abort(403)

            h.redirect_to(str('/dataset/%s#%s' % (
                c.pkg.name,
                'comment_' + res['id'] if success else ('comment_form' if comment_type == 'new' else 'reply_' + str(parent_id))
            )))

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
