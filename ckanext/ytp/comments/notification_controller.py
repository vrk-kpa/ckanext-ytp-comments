import ckan.authz as authz
import notification_helpers
import re

from ckan.lib.base import BaseController, abort


class NotificationController(BaseController):

    def valid_request_and_user(self, thread_or_comment_id):
        """
        Check user logged in and perform simple validation of id provided in request
        :param thread_or_comment_id:
        :return:
        """
        return False if not authz.auth_is_loggedin_user() \
            or not id \
            or self.contains_invalid_chars(thread_or_comment_id) else True

    def contains_invalid_chars(self, value):
        return re.search(r"[^0-9a-f-]", value)

    def follow(self, thread_or_comment_id=None):
        """
        Add the user to the list of comment notification email recipients
        :param thread_or_comment_id: A UUID - can be either a thread ID or a specific top level comment ID
        :return:
        """
        return self.follow_or_mute(thread_or_comment_id, 'follow')

    def mute(self, thread_or_comment_id=None):
        """
        Remove the user from the list of comment notification email recipients
        :param thread_or_comment_id: A UUID - can be either a thread ID or a specific top level comment ID
        :return:
        """
        return self.follow_or_mute(thread_or_comment_id, 'mute')

    def follow_or_mute(self, thread_or_comment_id, action):
        """
        *** Developers, please note: *** within YTP comments, a "thread" represents a set of comments for a given
        dataset or data request, whereas the meaning in the Jira story differs, i.e. it refers to a top level comment
        and it's subsequent replies. Where possible we use the code/YTP concept of "thread"

        :param thread_or_comment_id: UUID - can be either a thread ID (in the YTP sense) or a comment ID
        :param action: string - "follow" or "mute"
        :return:
        """
        if not self.valid_request_and_user(thread_or_comment_id):
            abort(404)

        thread, comment = notification_helpers.get_thread_comment_or_both(thread_or_comment_id)

        if not thread or (comment and not thread):
            abort(404)

        notification_level = 'content_item' if not comment else 'top_level_comment'

        user_id = notification_helpers.get_user_id()

        # Check for an existing record - helps us prevent re-adding the user to recipients table
        existing_record = notification_helpers.get_existing_record(user_id, thread.id, comment.id if comment else None)

        if action == 'follow':
            notification_helpers.process_follow_request(user_id, thread, comment, existing_record, notification_level)

        # User is muting comments at content item level or specific comment thread within that content item
        elif action == 'mute':
            notification_helpers.process_mute_request(user_id, thread, comment, existing_record, notification_level)
