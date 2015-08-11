# Globals
import datetime
import praw
import time
from slacker import Slacker
from util import retrieve_credentials

suspect_title_strings = ['?', 'help', 'stuck', 'why', 'my', 'feedback']
post_limit = 10


def post_is_suspicious(post_to_check):
    return \
        any(word in post_to_check.title.lower() for word in suspect_title_strings) \
        or post_to_check.domain == 'stackoverflow.com' \
        or (post_to_check.selftext and 'stackoverflow' in post_to_check.selftext.lower()) \
        or (post_to_check.selftext_html and any(block in post_to_check.selftext_html for block in ['<code', '%3Ccode']))


def notify_slack(submission):
    message = '========================'
    message += '\n\n*%s*' % submission.title
    message += '\n\nID: %s' % submission.id
    message += '\n\nComments link: %s' % submission.permalink
    if submission.url and 'www.reddit.com' not in submission.url:
        message += '\n\nPost link: %s' % submission.url
    if submission.selftext:
        message += '\n\n> %s' % submission.selftext.partition('\n')[0]
    slack.chat.post_message('#newposts', message, as_user='postbot')


credentials = retrieve_credentials()
channel_id = credentials['channel_id']

# Set up slack
slack = Slacker(credentials['slack_key'])

# Set up praw
r = praw.Reddit('androiddev_watcher by /u/pandanomic')
r.login(credentials['reddit_username'], credentials['reddit_pwd'], disable_warning=True)
subreddit = r.get_subreddit('androiddev')

now = datetime.datetime.utcnow()
now_minus_10 = now + datetime.timedelta(minutes=-10)
float_now = time.mktime(now_minus_10.timetuple())
print("Checking for new posts")
posts = [p for p in subreddit.get_new(limit=post_limit) if p.created_utc > float_now]
if len(posts) is 0:
    print("Nothing new")
else:
    print("Length is %s" % len(posts))
    for post in sorted(posts, key=lambda p: p.created_utc):
        notify_slack(post)
        print("Notified")