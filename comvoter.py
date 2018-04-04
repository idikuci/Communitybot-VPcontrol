#from steem import Steem
from piston.steem import Steem
from piston.account import Account
from piston.post import Post
import datetime
import time
import json

from keys import Posting_Key

accountname = 'idikuci'
#accountname = 'comedyopenmic'

nodes = ["wss://rpc.steemviz.com", "wss://rpc.steemliberator.com", "wss://steemd.minnowsupportproject.org"]
pattern = '%Y-%m-%dT%H:%M:%S'


MaxVP = 90
# cut off time in seconds [ 6 days X 24 hrs X 60 mins X 60 secs = 518400 seconds]
#cutofftime = 518400
# cut off time in seconds [ 5.5 days X 24 hrs X 60 mins X 60 secs = 475200 seconds]
cutofftime = 475200
# cut off time in seconds [ 5.5 days X 24 hrs X 60 mins X 60 secs = 432000 seconds]
cutofftime = 432000



def getactiveVP(account):
    """Calculates an account's active Voting Power(VP).
    Args:
        account: A Steem Account object.
    Returns:
        the active VP.
    """
    # Make sure we have the latest data
    account.refresh()
    tmpepochlastvote = 0
    # Get last 100 votes from account
    history = account.history2(filter_by='vote', take=100)
    for event in history:
        # Not really needed due to filter
        if(event['type'] == "vote"):
            # Make sure we are the one voting
            if(event['voter'] == account.name):
                epochlastvote = (time.mktime(time.strptime(event['timestamp'], pattern)))
                # History2 returns the history with oldest first. Keep going until latest vote
                tmpepochlastvote = epochlastvote

    epochlastvote = tmpepochlastvote
    timesincevote = (UtcNow()) - epochlastvote
    VP = account.voting_power() + ((timesincevote * (2000/86400)) / 100)
    # Make sure the voting power is max 100
    if(VP > 100):
        VP = 100
    return VP

def UtcNow():
    # Get current UTC time in seconds
    now = datetime.datetime.utcnow()
    return int(now.strftime("%s"))

def getupvotecandidate(account,s):
    """ Gets link to post/comment author has not voted on but is within voting window
    Args:
        account: A Steem Account object.
        s      : SteemInstance
    Returns:
        identifier of posts/comments within voting window not already voted on
    """
    # Make sure we have the latest data
    account.refresh()
    tmpepochlastvote = 0
    # Get last 2000 votes from account
    history = account.history2(filter_by='comment', take=2000)

    currenttime = UtcNow()
    oldest_id = []
    ignorepost = False
    for event in history:
       # Not really needed due to filter
        if(event['type'] == 'comment'):
            # Make sure we are the one voting
            if(event['author'] == account.name):
                epochlastvote = (time.mktime(time.strptime(event['timestamp'], pattern)))
                elapsedtime = currenttime - epochlastvote
                if elapsedtime < cutofftime: # Is post in within time limit (6.5days default)
                    identifier = "@" + event['author'] + "/" + event['permlink']
                    postid = Post(identifier,s) # Get comment info
                    for voterid in postid['active_votes']: # check if we have already voted
                        if (voterid['voter'] ==  account.name): # if already voted don't vote again
                            ignorepost = True
                            break
                    if not ignorepost:
                        oldest_id.append(identifier) # store link to posts




    return oldest_id






s = Steem(node=nodes)

upvoter = Steem(node=nodes, wif=Posting_Key)

# Initialize VP
account = Account(accountname, s)
VP = getactiveVP(account)

while True: # Loop continuously
    while VP < MaxVP: # If VP is below MaxVP go to sleep
        sleeptime = ( MaxVP - VP + 0.01 ) * (86400 / 20) # Time to sleep til we're above the MaxVP if no further votes are made
        print(" VP = " + str(VP) + "; Sleeptime = " + str(sleeptime) + ' Going to Sleep Now! NapTime!')

        time.sleep(sleeptime) # Sleep
        # Grab VP again
        account = Account(accountname, s)
        VP = getactiveVP(account)

    # Get oldest comment /post authored
    posts = getupvotecandidate(account,s)
    for post_ID in posts:
        try:
            print("voting on old post: " , post_ID)
            upvoter.vote(post_ID, 100, voter=accountname)
            print('Successfully Voted... See you in 10 Mins')
            time.sleep(600) # sleep for 10 minutes make sure we don't vote too  quickly and piston has time to update
        except:
            print("Already voted on this one try again")

        # If the VP is below desired level keep voting, else leave loop and go to sleep
        VP = getactiveVP(account)
        if VP < MaxVP:
            break




