import datetime
import ckan.plugins.toolkit as toolkit
import ckanext.ytp.comments.model as comment_model
import ckanext.ytp.comments.util as util
from ckan import logic
from ckan.lib.base import abort
import logging

from ckan.common import config
from ckanext.ytp.comments import helpers

log = logging.getLogger(__name__)


def comment_update(context, data_dict):
    model = context['model']

    logic.check_access("comment_update", context, data_dict)

    cid = logic.get_or_bust(data_dict, 'id')
    comment = comment_model.Comment.get(cid)
    if not comment:
        abort(404)

    # Validate that we have the required fields.
    if not all([data_dict.get('comment')]):
        raise logic.ValidationError("Comment text is required")

    # Cleanup the comment
    cleaned_comment = util.clean_input(data_dict.get('comment'))

    # Run profanity check
    if toolkit.asbool(config.get('ckan.comments.check_for_profanity', False)) \
            and (helpers.profanity_check(cleaned_comment) or helpers.profanity_check(data_dict.get('subject', ''))):
        raise logic.ValidationError("Comment blocked due to profanity.")

    comment.subject = data_dict.get('subject')
    comment.comment = cleaned_comment
    comment.modified_date = datetime.datetime.now()

    model.Session.add(comment)
    model.Session.commit()

    return comment.as_dict()
