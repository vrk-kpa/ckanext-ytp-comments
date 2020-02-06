import ckan.model as model
import logging

from ckan.lib.cli import CkanCommand

log = logging.getLogger(__name__)


class InitDBCommand(CkanCommand):
    """
    Initialises the database with the required tables
    Connects to the CKAN database and creates the comment
    and thread tables ready for use.
    """
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 0
    min_args = 0

    def __init__(self, name):
        super(InitDBCommand, self).__init__(name)

    def command(self):
        log.info("starting command")
        self._load_config()

        import ckan.model as model
        model.Session.remove()
        model.Session.configure(bind=model.meta.engine)

        import ckanext.ytp.comments.model as cmodel
        log.info("Initializing tables")
        cmodel.init_tables()
        log.info("DB tables are setup")


class InitNotificationsDB(CkanCommand):
    """Initialise the comment extension's notifications database tables
    """
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 0
    min_args = 0

    def command(self):
        self._load_config()

        model.Session.remove()
        model.Session.configure(bind=model.meta.engine)

        import notification_models
        notification_models.init_tables()
        log.debug("Comment notification preference DB table is setup")
