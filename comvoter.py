from piston.steem import Steem
from piston.account import Account
from piston.post import Post
import datetime
import calendar
import time

try: from keys import Posting_Key as posting_key
except: posting_key = ['PRIV POSTING KEY HERE']

accountname = 'ACC NAME HERE'

nodes = ["wss://steemd.minnowsupportproject.org",
         "wss://rpc.steemliberator.com",
         "wss://rpc.steemviz.com"]
pattern = '%Y-%m-%dT%H:%M:%S'



# cut off time in seconds
cutofftime = 432000
MaxVP = 97

def epochVote(e):
    return (time.mktime(time.strptime(e['timestamp'], pattern)))

def getactiveVP():
    """Calculates an account's active Voting Power(VP).
    Args:
        account: A Steem Account object.
    Returns:
        the active VP.
    """
    # Make sure we have the latest data
    account.refresh()
    epoch_last_vote = 0
    
    # Get last 100 votes from account
    history = account.history2(filter_by='vote', take=100)
    for event in history:
        # Not really needed due to filter
        if(event['type'] == "vote"):
            # Make sure we are the one voting
            if(event['voter'] == account.name):
                epoch_last_vote = epochVote(event)
    
    #get time since last vote sinve VP is updates upon vote
    timesincevote = epochDiff() - epoch_last_vote
    
    # calculate VP
    VP = account.voting_power() + ((timesincevote * (2000/86400)) / 100)
    
    # Make sure the voting power is max 100
    if(VP > 100): VP = 100
    
    return VP

def epochDiff():
    # Get current UTC time in seconds
    now = datetime.datetime.now()
    epoch = datetime.datetime(1970,1,1)
    epoch_diff = (now - epoch).total_seconds()
    return int(epoch_diff)

def getUpvoteCandidate():
    """ Gets link to post/comment author has not voted on but is within voting window
    Args:
        account: A Steem Account object.
        s      : SteemInstance
    Returns:
        identifier of posts/comments within voting window not already voted on
    """
    # Make sure we have the latest data
    account.refresh()
    epoch_last_vote = 0
    
    # Get last 2000 votes from account
    history = account.history2(filter_by='comment', take=2000)

    current_time = epochDiff()
    oldest_id = []
    
    for event in history:
        # Not really needed due to filter
        if(event['type'] == 'comment'):
            # Double confirmation of comment
            if event['permlink'].startswith("re-"):
                # Make sure we are the author
                if(event['author'] == accountname):
                    epoch_last_vote = epochVote(event)
                    elapsed_time = current_time - epoch_last_vote
                    # Is post in within time limit
                    if elapsed_time < cutofftime:
                        # Get comment info
                        identifier = "@" + event['author'] + "/" + event['permlink']
                        postid = Post(identifier,s)
                        # If we haven't already voted, add to list
                        if accountname not in postid['active_votes']:
                            oldest_id.append(identifier)
                        
    print(oldest_id)
    return oldest_id


s = Steem(node=nodes)
upvoter = Steem(node=nodes, wif=posting_key)
account = Account(accountname, s)

# Mainloop
while True:
    # Get current VP
    VP = getactiveVP()
    
    # If VP is below MaxVP go to sleep
    while VP < MaxVP:
        VP = getactiveVP()
        # Time to sleep til we're above the MaxVP if no further votes are made
        sleeptime = ( MaxVP - VP + 0.01 ) * (86400 / 20)
        
        print
        (
        " VP = " + str(VP) 
        + "; Sleeptime = " 
        + str(sleeptime) 
        + ' Going to Sleep Now! NapTime!'
        )

        if sleeptime > 0:
            time.sleep(sleeptime)

    # Get oldest comment /post authored
    posts = getUpvoteCandidate()
    
    # attempt to vote until success, then sleep for 10 min
    for post_ID in posts:
        try:
            print("voting on old post: " , post_ID)
            upvoter.vote(post_ID, 30, voter=accountname)
            print('Successfully Voted... See you in 10 Mins')
            break
        except Exception as e:
            print(e)
            
    time.sleep(600)