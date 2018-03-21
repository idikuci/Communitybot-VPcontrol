#from steem import Steem
from piston.steem import Steem
from piston.account import Account
import datetime
import time

import keys

#import sleep

nodes = ["wss://rpc.steemviz.com", "wss://rpc.steemliberator.com", "wss://steemd.minnowsupportproject.org"]
pattern = '%Y-%m-%dT%H:%M:%S'


MaxVP = 80
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
    history = account.history2(filter_by='comment', take=2000)
    print("candidate")
    print(history)

    tmpoldest = 0
    currenttime = UtcNow()

    for event in history:
        # Not really needed due to filter
       # print("event")
        if(event['type'] == 'comment'):
            # Make sure we are the one voting
            if(event['author'] == account.name):
                if (event['parent_author']):
                    epochlastvote = (time.mktime(time.strptime(event['timestamp'], pattern)))
                    elapsedtime = currenttime - epochlastvote
                    if elapsedtime < cutofftime:
#                        print(event)
                        if elapsedtime > tmpoldest:
                            tmpoldest = epochlastvote
                            oldest_id = event['permlink']
                            oldest_tags = event['json_metadata']
                            print(event)
                            post_detail = s.get_post('@' + account.name + '/' + oldest_id)
                            print(post_detail['voters'])




#                epochlastvote = (time.mktime(time.strptime(event['timestamp'], pattern)))
                # History2 returns the history with oldest first. Keep going until latest vote
#                tmpepochlastvote = epochlastvote

#    epochlastvote = tmpepochlastvote
#    timesincevote = (UtcNow()) - epochlastvote
#    VP = account.voting_power() + ((timesincevote * (2000/86400)) / 100)
    # Make sure the voting power is max 100
#    if(VP > 100):
#        VP = 100
    return 1






s = Steem(node=nodes)

upvoter = Steem(node=nodes, wif=Posting_Key) # idi

# Initialize VP
account = Account("idikuci", s)
VP = getactiveVP(account)

while True:
    while VP < MaxVP:
        sleeptime = ( MaxVP - VP ) * (86400 / 20)
        print(" VP = " + str(VP) + "; Sleeptime = " + str(sleeptime))

        time.sleep(sleeptime)
        account = Account("idikuci", s)
        VP = getactiveVP(account)

    # Get oldest comment /post authored
    post_ID = getupvotecandidate(account,s)
    print("voting on old post")
#    upvoter.vote(post_ID, 100, voter="comedyopenmic")

