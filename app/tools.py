import re


def contains_only_allowed_chars(string, allowed_chars):
    return re.fullmatch('[{}]+'.format(allowed_chars), string) is not None