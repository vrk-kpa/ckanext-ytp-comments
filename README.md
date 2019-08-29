ckanext-ytp-comments
====================

CKAN extension for adding comments to datasets. 

Anyone with an account can comment any public datasets. Users with modification access can delete comments from the dataset.

Some of the code is taken from [ckanext-comments](https://github.com/rossjones/ckanext-comments)


## Compatibility

Tested with CKAN 2.2 - 2.3

## Installation

Install to you ckan virtual environment

```
pip install -e  git+https://github.com/yhteentoimivuuspalvelut/ckanext-ytp-comments#egg=ckanext-ytp-comments
```

Add to ckan.ini

```
ckan.plugins = ... ytp_comments
```

Init db

```
paster --plugin=ckanext-ytp-comments initdb --config={ckan.ini}
```

## Email Notifications

The following config options can be added to the CKAN `.ini` file to enable email notifications whenever a new comment is added:

    ckan.comments.email_notifications_enabled = True

(defaults to `False`)

    ckan.comments.email_notification_to = author

Valid values are: `author` or `maintainer` defaults to `author` if incorrectly set, or not set and `ckan.comments.email_notifications_enabled = True`