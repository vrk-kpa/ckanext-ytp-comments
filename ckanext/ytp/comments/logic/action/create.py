import datetime
import ckan.plugins.toolkit as toolkit
import ckanext.ytp.comments.model as comment_model
import ckanext.ytp.comments.util as util
from ckan import logic
from ckan.common import config
from ckanext.ytp.comments import helpers
import logging

log = logging.getLogger(__name__)


def comment_create(context, data_dict):
    model = context['model']
    user = context['user']

    userobj = model.User.get(user)

    logic.check_access("comment_create", context, data_dict)

    # Validate that we have the required fields.
    if not all([data_dict.get('comment')]):
        raise logic.ValidationError("Comment text is required")

    thread_id = data_dict.get('thread_id')

    if not thread_id:
        url = data_dict.get('url')
        if url:
            thread = comment_model.CommentThread.from_url(url)
            thread_id = thread.id if thread else None

    if not thread_id:
        raise logic.ValidationError("Thread identifier or URL is required")

    # Cleanup the comment
    cleaned_comment = util.clean_input(data_dict.get('comment'))

    # Run profanity check
    if toolkit.asbool(config.get('ckan.comments.check_for_profanity', False)) \
            and (helpers.profanity_check(cleaned_comment) or helpers.profanity_check(data_dict.get('subject', ''))):
        raise logic.ValidationError({"message": "Comment blocked due to profanity."})

    # Create the object
    cmt = comment_model.Comment(thread_id=thread_id,
                                comment=cleaned_comment)
    cmt.user_id = userobj.id
    cmt.subject = data_dict.get('subject', 'No subject')

    if 'creation_date' in context:
        cmt.creation_date = datetime.datetime.fromtimestamp(context['creation_date'])

    # Check if there is a parent ID and that it is valid
    # TODO, validity in this case includes checking parent is not
    # deleted.
    prt = data_dict.get('parent_id')
    if prt:
        parent = comment_model.Comment.get(prt)
        if parent:
            cmt.parent_id = parent.id

    # approval and spam checking removed

    model.Session.add(cmt)
    model.Session.commit()

    return cmt.as_dict()
