from ckan.common import config


def maximum_thread_depth():
    return config.get('ckan.comments.maximum_thread_depth', 999)
