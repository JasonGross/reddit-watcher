#!/usr/bin/env python3
# REQUIREMENTS: pip install requests
import requests
import time
import sys
import itertools
import os
from datetime import datetime, timedelta

__all__ = ['SUBREDDITS', 'REFRESH_RATE_IN_SECONDS', 'set_subreddits', 'set_refresh_rate', 'refresh_sleep']

SUBREDDITS = [{'name': 'slatestarcodex',
               # alert when the top post is at least this old
               'top_post_min_age': {'hours': 12},
               # alert when there exists a post newer than MAX_AGE with at least MIN_UPVOTES upvotes
               'recent_posts_max_age': {'hours': 1},
               'recent_posts_min_upvotes': 200},
              {'name': 'LessWrong',
               # alert when the top post is at least this old
               'top_post_min_age': {'hours': 12},
               # alert when there exists a post newer than MAX_AGE with at least MIN_UPVOTES upvotes
               'recent_posts_max_age': {'hours': 1},
               'recent_posts_min_upvotes': 200},
              {'name': 'rational',
               # alert when the top post is at least this old
               'top_post_min_age': {'hours': 12},
               # alert when there exists a post newer than MAX_AGE with at least MIN_UPVOTES upvotes
               'recent_posts_max_age': {'hours': 1},
               'recent_posts_min_upvotes': 200},
              {'name': 'nyc',
               # alert when the top post is at least this old
               'top_post_min_age': {'hours': 12},
               # alert when there exists a post newer than MAX_AGE with at least MIN_UPVOTES upvotes
               'recent_posts_max_age': {'hours': 1},
               'recent_posts_min_upvotes': 200}]


def set_subreddits(v):
    global SUBREDDITS
    SUBREDDITS = v


REFRESH_RATE_IN_SECONDS = 10 * 60  # 10 minutes


def set_refresh_rate(v):
    global REFRESH_RATE_IN_SECONDS
    REFRESH_RATE_IN_SECONDS = v


REDDIT_TOP_URL = 'https://www.reddit.com/r/%s/top.json?limit=100'
REDDIT_NEW_URL = 'https://www.reddit.com/r/%s/new.json?limit=100'


# https://stackoverflow.com/a/287944/377022
class bcolors:
    HEADER = '\033[95m'
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    NORMAL = '\x1b[m\x0f'  # python -c "print(repr('$(tput sgr0)'))"


# play the terminal bell
ALERT_STRING = '\a'


def clearscreen():
    os.system('cls' if os.name == 'nt' else 'clear')


def get_url(url, after=None):
    # as a reminder to developers, we recommend that clients make no
    # more than <a href="http://github.com/reddit/reddit/wiki/API">one
    # request every two seconds</a> to avoid seeing this message.
    time.sleep(2)
    after_str = '' if after is None else f'&after={after}'
    result = requests.get(f'{url}{after_str}', headers={'user-agent': 'reddit-watcher/0.0.1'}).json()['data']
    for child in result['children']: yield child['data']
    if result['after'] is not None:
        for child in get_url(url, after=result['after']): yield child


def get_post_date(post):
    return datetime.fromtimestamp(post['created_utc'])


def get_upvote_count(post):
    return post['ups'] - post['downs']


def make_bold_console(s): return f'{bcolors.BOLD}{s}{bcolors.NORMAL}'
def make_red_console(s): return f'{bcolors.RED}{s}{bcolors.ENDC}'
def make_green_console(s): return f'{bcolors.GREEN}{s}{bcolors.ENDC}'


PREV_ALERTED_DATA = {sr['name']: {'top': None, 'new': None} for sr in SUBREDDITS}
def get_alerts(subreddit, make_bold, make_red, make_green):
    yield make_bold(f'subreddit {subreddit["name"]}:')
    for top in itertools.islice(get_url(REDDIT_TOP_URL % subreddit['name']), 1):  # if there are no top posts, don't error
        top_date = get_post_date(top)
        top_age = datetime.now() - top_date
        if top_age < timedelta(**subreddit['top_post_min_age']):  # there's a new post!
            if PREV_ALERTED_DATA[subreddit['name']]['top'] != top['title']:
                yield make_red(f'Top Post in {subreddit["name"]} is new (age = {top_age}) ({top_date}): {top["title"]} (https://reddit.com/{top["permalink"]})')
                yield ALERT_STRING
            else:
                yield make_red(f'Top Post in {subreddit["name"]} (age = {top_age}) ({top_date}): {top["title"]} (https://reddit.com/{top["permalink"]})')
            PREV_ALERTED_DATA[subreddit['name']]['top'] = top['title']
        else:
            yield make_green(f'Top Post in {subreddit["name"]} (age = {top_age}) ({top_date}): {top["title"]} (https://reddit.com/{top["permalink"]})')
    found_new = False
    count_new = 0
    max_upvotes = None
    for post in get_url(REDDIT_NEW_URL % subreddit['name']):
        post_date = get_post_date(post)
        post_age = datetime.now() - post_date
        if post_age <= timedelta(**subreddit['recent_posts_max_age']):  # there's a new post!
            count_new += 1
            upvotes = get_upvote_count(post)
            max_upvotes = max(upvotes, max_upvotes) if max_upvotes is not None else upvotes
            if upvotes >= subreddit['recent_posts_min_upvotes']:  # with a lot of upvotes!
                found_new = True
                if PREV_ALERTED_DATA[subreddit['name']]['new'] != post['title']:
                    yield make_red(f'New Post in {subreddit["name"]} is newly (age = {post_age}) ({top_date}) upvoted ({upvotes}): {top["title"]} (https://reddit.com/{top["permalink"]})')
                    yield ALERT_STRING
                else:
                    yield make_red(f'New Post in {subreddit["name"]} (age = {post_age}) ({top_date}) is upvoted ({upvotes}): {top["title"]} (https://reddit.com/{top["permalink"]})')
                PREV_ALERTED_DATA[subreddit['name']]['new'] = post['title']
            else:
                continue
        else:
            break
    if not found_new:
        PREV_ALERTED_DATA[subreddit['name']]['new'] = None
        yield make_green(f'All {count_new} recent (<= {timedelta(**subreddit["recent_posts_max_age"])}) posts in {subreddit["name"]} have less than {subreddit["recent_posts_min_upvotes"]} upvotes (max = {max_upvotes})')


def get_all_alerts(*args, **kwargs):
    for subreddit in SUBREDDITS:
        for line in get_alerts(subreddit, *args, **kwargs):
            yield line


def cleartext_console():
    if sys.stdout.isatty():
        clearscreen()


def alert_console(): print(ALERT_STRING, end='')


def printline_console(s): print(s)


def refresh(cleartext, alert, printline, printsleep, make_bold, make_red, make_green):
    cleartext()
    for line in get_all_alerts(make_bold=make_bold_console, make_red=make_red_console, make_green=make_green_console):
        if line == ALERT_STRING: alert()
        else: printline(line)


def refresh_sleep(cleartext, alert, printline, printsleep, make_bold, make_red, make_green):
    cur_time = time.time()
    refresh(cleartext=cleartext, alert=alert, printline=printline, printsleep=printsleep, make_bold=make_bold, make_red=make_red, make_green=make_green)
    sleep_time = max(2, REFRESH_RATE_IN_SECONDS - int(time.time() - cur_time))
    printsleep(f'Sleeping for {timedelta(seconds=sleep_time)}, next update at {datetime.now() + timedelta(seconds=sleep_time)}...')
    time.sleep(sleep_time)


def refresh_sleep_console():
    refresh_sleep(cleartext=cleartext_console, alert=alert_console, printline=printline_console, printsleep=printline_console,
                  make_bold=make_bold_console, make_red=make_red_console, make_green=make_green_console)


if __name__ == '__main__':
    while True:
        refresh_sleep_console()

# TODO: consider using praw
# maybe import praw
# reddit = praw.Reddit(user_agent='reddit-watcher/0.0.1', client_id='reddit-watcher/0.0.1', client_secret=None)
