import os, re

class Resources:

    APP_NAME = "HipScud"
    SIGNIN_URL = "https://www.hipchat.com/sign_in"
    HOMEPAGE_URL_RE = re.compile(r'^http[s]://[a-zA-Z0-9_\-\.]+/home')
    CHAT_URL_RE = re.compile(r'^http[s]://[a-zA-Z0-9_\-\.]+/chat')

    SPELL_DICT_PATH = "/usr/share/hunspell/"
    SPELL_LIMIT = 6

    # It's initialized in /hipscud script
    INSTALL_DIR = os.path.dirname(os.path.realpath(__file__))

    def get_path(filename):
        return os.path.join(Resources.INSTALL_DIR, 'resources', filename)
