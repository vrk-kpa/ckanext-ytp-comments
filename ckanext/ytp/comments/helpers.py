from ckan.common import config
from profanityfilter import ProfanityFilter


def profanity_check(cleaned_comment):
    more_words = load_bad_words()

    pf = ProfanityFilter(extra_censor_list=more_words)
    return pf.is_profane(cleaned_comment)


def load_bad_words():
    filepath = config.get('ckan.comments.bad_words_file', None)
    if not filepath:
        import os
        filepath = os.path.dirname(os.path.realpath(__file__)) + '/bad_words.txt'
    f = open(filepath, 'r')
    x = f.read().splitlines()
    f.close()
    return x
