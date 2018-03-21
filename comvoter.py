#from steem import Steem
from piston.steem import Steem
from piston.account import Account
import datetime
import time

from keys import Posting_Key

#import sleep

nodes = ["wss://rpc.steemviz.com", "wss://rpc.steemliberator.com", "wss://steemd.minnowsupportproject.org"]
pattern = '%Y-%m-%dT%H:%M:%S'


MaxVP = 97
# cutt off time in seconds [ 6 days X 24 hrs X 60 mins X 60 secs = 518400seconds]
cutofftime = 518400


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
        permlink of oldest post within voting window not already voted on
    """
    # Make sure we have the latest data
    account.refresh()
    tmpepochlastvote = 0
    # Get last 100 votes from account
    history = account.history2(filter_by='comment', take=2000)
#    print("candidate")
#    print(history)


    voteshistory = account.history2(filter_by='vote', take=2000)
    # Get list of things We've already voted on
    votedlist = []
    for event in voteshistory:
       # Not really needed due to filter
        if(event['type'] == "vote"):
            # Make sure we are the one voting
            if(event['voter'] == account.name):
                votedlist.append(event['permlink'])

    tmpoldest = 0
    currenttime = UtcNow()

    for event in history:
       # Not really needed due to filter
       # print("event")
        if(event['type'] == 'comment'):
            # Make sure we are the one voting
            if(event['author'] == account.name):
                if (event['parent_author']): # If it's a comment
                    if (event['permlink'] not in votedlist):
                        # Time of post
                        epochlastvote = (time.mktime(time.strptime(event['timestamp'], pattern)))
                        elapsedtime = currenttime - epochlastvote
                        if elapsedtime < cutofftime: # Is post in within time limit (6.5days default)
                   #         print(event)
                            if elapsedtime > tmpoldest: # if it's the oldest we've found
                                tmpoldest = epochlastvote
                                oldest_id = "@" + event['author'] + "/" + event['permlink'] # get link to oldest post




    return oldest_id






s = Steem(node=nodes)

upvoter = Steem(node=nodes, wif=Posting_Key)

# Initialize VP
account = Account("idikuci", s)
VP = getactiveVP(account)

while True: # Loop continuously
    while VP < MaxVP: # If VP is below MaxVP go to sleep
        sleeptime = ( MaxVP - VP ) * (86400 / 20) # Time to sleep tile we're above the MaxVP if no further votes are made
        print(" VP = " + str(VP) + "; Sleeptime = " + str(sleeptime))

        time.sleep(sleeptime) # Sleep
        # Grab VP again
        account = Account("idikuci", s)
        VP = getactiveVP(account)

    # Get oldest comment /post authored
    post_ID = getupvotecandidate(account,s)
    print("voting on old post: " , post_ID)
    upvoter.vote(post_ID, 100, voter="idikuci")
    time.sleep(600)

