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

## Follow / Mute comments

Comment notifications (via email) are managed by opt-in, i.e. without opting in to receive comment notifications at the content item or thread level, only authors or organisation admins will receive email notifications. 

This feature allows users to following or mute comments at the content item level or for a specific comment thread on the content item.

When a user follows comments on a content item or content item thread they will receive email notifications when new comments or replies are posted.

### Setup

1. Initialise the comment notification receipients database table, e.g.

        cd /usr/lib/ckan/default/src/ckanext-ytp-comments # Your PATH may vary
        
        paster init_notifications_db -c /etc/ckan/default/development.ini # Use YOUR path and relevant CKAN .ini file

    This will create a new table in the CKAN database named `comment_notification_recipient` that holds the status of individual user's follow or mute preferences.
    
    *Note:* if your deployment process does not run `python setup.py develop` after deploying code changes for extensions, you may need to run this in order for paster to recognise the `init_notifications_db` command:

        python setup.py develop

2. Add the following config setting to your CKAN `.ini` file:

        ckan.comments.follow_mute_enabled = True

3. Restart CKAN
