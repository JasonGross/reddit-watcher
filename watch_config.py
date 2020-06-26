import os, json, sys, logging
import watch
from datetime import datetime, timedelta

__all__ = ['CONF_FILE', 'CONFIG_VERSION', 'load_configuration', 'save_configuration']

# https://stackoverflow.com/a/42615559/377022
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS'.
    #
    # Using sys._MEIPASS does not work for one-file executables. From
    # the docs: For a one-folder bundle, this is the path to that
    # folder, wherever the user may have put it. For a one-file bundle,
    # this is the path to the _MEIxxxxxx temporary folder created by the
    # bootloader . Use sys.executable for one-file executables
    application = sys.executable
else:
    application = __file__

CONF_FILE = os.path.join(os.path.dirname(os.path.abspath(application)), 'reddit-watcher-conf.ini')

CONFIG_VERSION = '0.0.1'

def get_current_configuration():
    return {'CONFIG_VERSION': CONFIG_VERSION,
            'SUBREDDITS': {'description': 'The list of subreddits and the data about them',
                           'value': watch.SUBREDDITS},
            'REFRESH_RATE': {'description': 'How often to re-poll reddit and refresh the display (in seconds)',
                             'value': watch.REFRESH_RATE_IN_SECONDS}}

def validate_subreddits(subs):
    if subs is None: return False
    for s in subs:
        for k, ty in (('name', str), ('recent_posts_min_upvotes', int)):
            if k not in s.keys():
                logging.error(f'Invalid configuration: missing key "{k}" in subreddit value {s}')
                return False
            if not isinstance(s[k], ty):
                logging.error(f'Invalid configuration: {k} of subreddit is not a {ty}: {s}')
                return False
        for k in ('top_post_min_age', 'recent_posts_max_age'):
            if k not in s.keys():
                logging.error(f'Invalid configuration: missing key "{k}" in subreddit value {s}')
                return False
            try:
                t = timedelta(**(s[k]))
            except Exception as e:
                logging.error(f'Invalid configuration: key "{k}" does not contain valid arguments to timedelta ({e}): timedelta(**{s[k]})')
                return False
    return True

def validate_refresh(refresh):
    if refresh is None: return False
    if not isinstance(refresh, int):
        logging.error(f'Invalid configuration: refresh rate is not an integer: {refresh}')
        return False
    return True

def update_with_configuration(config):
    if 'CONFIG_VERSION' not in config.keys():
        logging.error(f'Invalid configuration (missing key CONFIG_VERSION):\n{config}')
        return
    if config['CONFIG_VERSION'] == CONFIG_VERSION:
        sr = None
        try:
            sr = config['SUBREDDITS']['value']
        except Exception as e:
            logging.error(f'Invalid configuration (exception in config["SUBREDDITS"]["value"]: {e}):\n{config}')
        if validate_subreddits(sr): watch.SUBREDDITS = sr
        refresh = None
        try:
            refresh = config['REFRESH_RATE']['value']
        except Exception as e:
            logging.error(f'Invalid configuration (exception in config["REFRESH_RATE"]["value"]: {e}):\n{config}')
        if validate_refresh(refresh): watch.REFRESH_RATE_IN_SECONDS = refresh

def backup(fname, bak='.bak'):
    if bak is None: return
    if os.path.exists(fname + bak): backup(fname + bak, bak=bak)
    os.rename(fname, fname + bak)

def save_file(contents, fname, bak='.bak'):
    if os.path.exists(fname):
        with open(fname, 'r') as f:
            cur_contents = f.read()
        if cur_contents != contents: backup(fname, bak=bak)
    with open(fname, 'w') as f:
        f.write(contents)

def save_configuration():
    save_file(json.dumps(get_current_configuration(), sort_keys=True, indent=2), CONF_FILE)

def load_configuration():
    try:
        with open(CONF_FILE, 'r') as f:
            update_with_configuration(json.load(f))
    except Exception as e:
        logging.error(f'Invalid configuration: {e}')
    save_configuration()
