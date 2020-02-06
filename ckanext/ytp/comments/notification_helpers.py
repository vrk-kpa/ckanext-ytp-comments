import ckan.model as model
import ckan.plugins.toolkit as toolkit
import logging
import sqlalchemy

from ckan.common import config
from model import Comment, CommentThread
from notification_models import CommentNotificationRecipient

_and_ = sqlalchemy.and_
log = logging.getLogger(__name__)


def comment_notification_recipients_enabled():
    return config.get('ckan.comments.follow_mute_enabled', False)


def get_thread_comment_or_both(thread_or_comment_id):
    """
    Determine if provided ID is for a thread or comment
    :param thread_or_comment_id: UUID - can be either a thread ID (in the YTP sense) or a comment ID
    :return: CommentThread object, and Comment object (if applicable)
    """
    thread = CommentThread.get(thread_or_comment_id)

    if thread:
        comment = None
    else:
        # Fallback: check for comment by id provided...
        comment = Comment.get(thread_or_comment_id)
        if comment:
            thread = CommentThread.get(comment.thread_id)

    return thread, comment


def get_existing_record(user_id, thread_id, comment_id=None):
    # Condition doesn't seem to get set properly within _and_ filter
    if not comment_id:
        comment_id = u''

    record = (
        model.Session.query(
            CommentNotificationRecipient
        )
        .filter(
            _and_(
                CommentNotificationRecipient.user_id == user_id,
                CommentNotificationRecipient.thread_id == thread_id,
                CommentNotificationRecipient.comment_id == comment_id
            )
        )
    ).first()

    return record


def get_comment_notification_records_for_user(user_id, thread_id):
    try:
        records = (
            model.Session.query(
                CommentNotificationRecipient
            )
            .filter(
                _and_(
                    CommentNotificationRecipient.user_id == user_id,
                    CommentNotificationRecipient.thread_id == thread_id
                )
            )
        )
        return records
    except Exception, e:
        log.error('Unable to retrieve comment notification statuses')
        log.error(str(e))


def get_user_comment_follow_mute_status(user_id, content_item_thread_id):
    following_content_item = False
    comments_following = []
    comments_muted = []

    for record in get_comment_notification_records_for_user(user_id, content_item_thread_id):
        if record.comment_id == u'':
            following_content_item = True
        elif record.action == 'follow':
            comments_following.append(record.comment_id)
        elif record.action == 'mute':
            comments_muted.append(record.comment_id)

    return following_content_item, comments_following, comments_muted


def remove_comment_notification_record(record):
    try:
        model.Session.delete(record)
        model.Session.commit()
    except Exception, e:
        log.error('Error removing `comment_notification_recipient` record:')
        log.error(str(e))


def remove_existing_follows_for_user(user_id, thread_id):
    follows = get_comment_notification_records_for_user(user_id, thread_id)
    for record in follows:
        remove_comment_notification_record(record)


def add_comment_notification_record(user_id, thread_id, comment_id, notification_level, action):
    data_dict = {
        'user_id': user_id,
        'thread_id': thread_id,
        'comment_id': comment_id,
        'notification_level': notification_level,
        'action': action
    }
    try:
        model.Session.add(CommentNotificationRecipient(**data_dict))
        model.Session.commit()
    except Exception, e:
        log.error('Error adding `comment_notification_recipient` record:')
        log.error(str(e))


def add_user_to_comment_notifications(user_id, thread_id, comment_id=u''):
    # Is the user attempting to follow at the dataset/data request or the comment level?
    notification_level = 'top_level_comment' if comment_id else 'content_item'
    add_comment_notification_record(user_id, thread_id, comment_id, notification_level, 'follow')


def add_commenter_to_comment_notifications(user_id, thread_id, comment_id=u''):
    existing_record = get_existing_record(user_id, thread_id, comment_id)
    if existing_record and existing_record.action == 'mute':
        remove_comment_notification_record(existing_record)
        add_user_to_comment_notifications(user_id, thread_id, comment_id)
    elif not existing_record or (existing_record and existing_record.action != 'follow'):
        add_user_to_comment_notifications(user_id, thread_id, comment_id)


def mute_comment_thread_for_user(user_id, thread_id, comment_id):
    add_comment_notification_record(user_id, thread_id, comment_id, 'top_level_comment', 'mute')


def process_follow_request(user_id, thread, comment, existing_record, notification_level):

    following_content_item, \
        comments_following, \
        comments_muted = get_user_comment_follow_mute_status(
            user_id,
            thread.id
        )

    if notification_level == 'content_item':
        # Check if user already following comments at content item level
        if following_content_item:
            return 'User already following comments at content item level'
        else:
            add_user_to_comment_notifications(user_id, thread.id)
    else:
        if comment.id in comments_following:
            return 'User already following thread'
        else:
            if comment.id in comments_muted and existing_record and existing_record.action == 'mute':
                # Remove existing mute record
                remove_comment_notification_record(existing_record)
            # If user is following comments at content item level and no mute record in place,
            # there is no need to add follow record for specific comment thread..
            if not following_content_item:
                add_user_to_comment_notifications(user_id, thread.id, comment.id)


def process_mute_request(user_id, thread, comment, existing_record, notification_level):

    following_content_item, \
        comments_following, \
        comments_muted = get_user_comment_follow_mute_status(
            user_id,
            thread.id
        )

    if notification_level == 'content_item':
        # When user mutes comments at content item level we remove ALL existing records for that user
        # in the `comment_notification_recipient` table for the matching YTP thread.id
        remove_existing_follows_for_user(user_id, thread.id)
        return 'Comments muted at content item level for user'
    elif comment.id in comments_muted:
        return 'Thread already muted for user'
    else:
        if comment.id in comments_following and existing_record and existing_record.action == 'follow':
            # Remove existing follow record
            remove_comment_notification_record(existing_record)
        # Only need to add mute record if user is following comments at content item level
        if comment.id not in comments_muted and following_content_item:
            mute_comment_thread_for_user(user_id, thread.id, comment.id)

        return 'Thread muted for user'


def get_comment_notification_recipients(action, user_email, thread_id, comment_id=None):
    try:
        if not comment_id:
            comment_id = u''

        session = model.Session
        emails = (
            session.query(
                model.User.email
            )
            .join(
                CommentNotificationRecipient,
                CommentNotificationRecipient.user_id == model.User.id
            )
            .filter(CommentNotificationRecipient.thread_id == thread_id)
            .filter(CommentNotificationRecipient.comment_id == comment_id)
            .filter(CommentNotificationRecipient.action == action)
            .filter(model.User.email != user_email)
            .group_by(model.User.email)
        )
        return [email[0] for email in emails.all()]
    except Exception, e:
        log.error('Exception raised in `get_comment_notification_recipients`')
        log.error(str(e))
    return []


def get_content_item_followers(user_email, thread_id):
    return get_comment_notification_recipients('follow', user_email, thread_id)


def get_top_level_comment_followers(user_email, thread_id, comment_id):
    return get_comment_notification_recipients('follow', user_email, thread_id, comment_id)


def get_top_level_comment_mutees(thread_id, comment_id):
    return get_comment_notification_recipients('mute', None, thread_id, comment_id)


def get_comment_notification_recipients_enabled():
    return config.get('ckan.comments.follow_mute_enabled', False)


def get_user_id():
    user = toolkit.c.userobj
    return user.id
