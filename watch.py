#!/usr/bin/env python3
# REQUIREMENTS: pip install requests
import requests, time, re, sys, itertools, os
from datetime import datetime, timedelta

SUBREDDITS = [{'name': 'slatestarcodex',
               # alert when the top post is at least this old
               'top_post_min_age': timedelta(hours=12),
               # alert when there exists a post newer than MAX_AGE with at least MIN_UPVOTES upvotes
               'recent_posts_max_age': timedelta(hours=1),
               'recent_posts_min_upvotes': 200},
              {'name': 'LessWrong',
               # alert when the top post is at least this old
               'top_post_min_age': timedelta(hours=12),
               # alert when there exists a post newer than MAX_AGE with at least MIN_UPVOTES upvotes
               'recent_posts_max_age': timedelta(hours=1),
               'recent_posts_min_upvotes': 200},
              {'name': 'rational',
               # alert when the top post is at least this old
               'top_post_min_age': timedelta(hours=12),
               # alert when there exists a post newer than MAX_AGE with at least MIN_UPVOTES upvotes
               'recent_posts_max_age': timedelta(hours=1),
               'recent_posts_min_upvotes': 200},
              {'name': 'nyc',
               # alert when the top post is at least this old
               'top_post_min_age': timedelta(hours=12),
               # alert when there exists a post newer than MAX_AGE with at least MIN_UPVOTES upvotes
               'recent_posts_max_age': timedelta(hours=1),
               'recent_posts_min_upvotes': 200}]

REFRESH_RATE_IN_SECONDS = 10 * 60 # 10 minutes

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
    NORMAL = '\x1b[m\x0f' # python -c "print(repr('$(tput sgr0)'))"

def alert():
    # play the terminal bell
    print('\a', end='')

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

PREV_ALERTED_DATA = {sr['name']: {'top': None, 'new': None} for sr in SUBREDDITS}
def update_with_alerts(subreddit):
    print(f'{bcolors.BOLD}subreddit {subreddit["name"]}:{bcolors.NORMAL}')
    for top in itertools.islice(get_url(REDDIT_TOP_URL % subreddit['name']), 1): # if there are no top posts, don't error
        top_date = get_post_date(top)
        top_age = datetime.now() - top_date
        if top_age < subreddit['top_post_min_age']: # there's a new post!
            if PREV_ALERTED_DATA[subreddit['name']]['top'] != top['title']:
                print(f'{bcolors.RED}Top Post in {subreddit["name"]} is new (age = {top_age}) ({top_date}): {top["title"]} (https://reddit.com/{top["permalink"]}){bcolors.ENDC}')
                alert()
            else:
                print(f'{bcolors.RED}Top Post in {subreddit["name"]} (age = {top_age}) ({top_date}): {top["title"]} (https://reddit.com/{top["permalink"]}){bcolors.ENDC}')
            PREV_ALERTED_DATA[subreddit['name']]['top'] = top['title']
        else:
            print(f'{bcolors.GREEN}Top Post in {subreddit["name"]} (age = {top_age}) ({top_date}): {top["title"]} (https://reddit.com/{top["permalink"]}){bcolors.ENDC}')
    found_new = False
    count_new = 0
    max_upvotes = None
    for post in get_url(REDDIT_NEW_URL % subreddit['name']):
        post_date = get_post_date(post)
        post_age = datetime.now() - post_date
        if post_age <= subreddit['recent_posts_max_age']: # there's a new post!
            count_new += 1
            upvotes = get_upvote_count(post)
            max_upvotes = max(upvotes, max_upvotes) if max_upvotes is not None else upvotes
            if upvotes >= subreddit['recent_posts_min_upvotes']: # with a lot of upvotes!
                found_new = True
                if PREV_ALERTED_DATA[subreddit['name']]['new'] != post['title']:
                    print(f'{bcolors.RED}New Post in {subreddit["name"]} is newly (age = {post_age}) ({top_date}) upvoted ({upvotes}): {top["title"]} (https://reddit.com/{top["permalink"]}){bcolors.ENDC}')
                    alert()
                else:
                    print(f'{bcolors.RED}New Post in {subreddit["name"]} (age = {post_age}) ({top_date}) is upvoted ({upvotes}): {top["title"]} (https://reddit.com/{top["permalink"]}){bcolors.ENDC}')
                PREV_ALERTED_DATA[subreddit['name']]['new'] = post['title']
            else:
                continue
        else:
            break
    if not found_new:
        PREV_ALERTED_DATA[subreddit['name']]['new'] = None
        print(f'{bcolors.GREEN}All {count_new} recent (<= {subreddit["recent_posts_max_age"]}) posts in {subreddit["name"]} have less than {subreddit["recent_posts_min_upvotes"]} upvotes (max = {max_upvotes}){bcolors.ENDC}')

def refresh():
    clearscreen()
    for subreddit in SUBREDDITS:
        update_with_alerts(subreddit)

if __name__ == '__main__':
    while True:
        cur_time = time.time()
        refresh()
        sleep_time = max(2, REFRESH_RATE_IN_SECONDS - int(time.time() - cur_time))
        print(f'Sleeping for {timedelta(seconds=sleep_time)}, next update at {datetime.now() + timedelta(seconds=sleep_time)}...')
        time.sleep(sleep_time)

# TODO: consider using praw
#import praw
#reddit = praw.Reddit(user_agent='reddit-watcher/0.0.1', client_id='reddit-watcher/0.0.1', client_secret=None)
