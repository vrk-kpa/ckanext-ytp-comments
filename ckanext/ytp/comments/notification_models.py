import ckan.model as model
import datetime

from sqlalchemy import Table, Column, MetaData
from sqlalchemy import types
from sqlalchemy.orm import mapper
from ckan.model.types import make_uuid

log = __import__('logging').getLogger(__name__)

metadata = MetaData()


class CommentNotificationRecipient(object):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.id = make_uuid()
        self.timestamp = datetime.datetime.utcnow()


comment_notification_recipient_table = Table('comment_notification_recipient', metadata,
                                             Column('id', types.UnicodeText, primary_key=True,
                                                    default=make_uuid),
                                             Column('timestamp', types.DateTime, default=datetime.datetime.utcnow()),
                                             Column('user_id', types.UnicodeText),
                                             Column('thread_id', types.UnicodeText),
                                             Column('comment_id', types.UnicodeText, default=u''),
                                             Column('notification_level', types.UnicodeText),
                                             Column('action', types.UnicodeText)
                                             )
mapper(CommentNotificationRecipient, comment_notification_recipient_table)


def init_tables():
    metadata.create_all(model.meta.engine)
