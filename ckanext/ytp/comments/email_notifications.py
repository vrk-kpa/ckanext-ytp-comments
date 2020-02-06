import ckan.lib.mailer as mailer
import ckan.logic as logic
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import logging

from ckan.common import config
from ckan.lib.base import render_jinja2


log1 = logging.getLogger(__name__)
NotFound = logic.NotFound


def get_dataset_owner_email(dataset_id):
    """
    Returns the email address of the dataset author or maintainer
    :param dataset_id: string
    :return: string of dataset author or maintainer email address
    """
    context = {'model': model}
    dataset = logic.get_action('package_show')(context, {'id': dataset_id})

    email_notification_to = config.get('ckan.comments.email_notification_to')

    if not email_notification_to or email_notification_to not in ['author', 'maintainer']:
        email_notification_to = 'author'

    return dataset.get(email_notification_to + '_email', None) if dataset else None


def send_email(to, subject, msg):
    """
    Use CKAN mailer logic to send an email to an individual email address

    :param to: string
    :param subject: string
    :param msg: string
    :return:
    """
    # Attempt to send mail.
    mail_dict = {
        'recipient_email': to,
        'recipient_name': to,
        'subject': subject,
        'body': msg,
        'headers': {'reply-to': config.get('smtp.mail_from')}
    }

    try:
        mailer.mail_recipient(**mail_dict)
    except mailer.MailerException:
        log1.error(u'Cannot send email notification to %s.', to, exc_info=1)


def send_notification_emails(users, template, extra_vars):
    """
    Sets the email body and sends an email notification to each user in the list provided

    :param users: list of user email addresses to receive the notification
    :param template: string indicating which email template to use
    :param extra_vars: dict
    :return:
    """
    if users:
        subject = render_jinja2('emails/subjects/{0}.txt'.format(template), extra_vars)
        body = render_jinja2('emails/bodies/{0}.txt'.format(template), extra_vars)

        for user in users:
            toolkit.enqueue_job(send_email, [user, subject, body], title=u'Comment Email')
    return users


def notify_admin(template, content_item_id, comment_id):
    """
    :param template: string indicating which email template to use
    :param content_item_id: UUID of the content item
    :param comment_id: ID of the comment submitted (used in URL of email body)
    :return:
    """
    owner_email = get_dataset_owner_email(content_item_id)
    admin_user = [owner_email] if owner_email else []

    if admin_user:
        send_notification_emails(
            admin_user,
            template,
            {
                'url': get_content_item_link(content_item_id, comment_id)
            }
        )


def get_content_item_link(content_item_id, comment_id=None):
    """
    Get a fully qualified URL to the content item being commented on.

    :param content_item_id: string Package name, or Data Request ID
    :param comment_id: string `comment`.`id`
    :return:
    """
    url = toolkit.url_for('dataset_read', id=content_item_id, qualified=True)
    if comment_id:
        url += '#comment_' + str(comment_id)
    return url
