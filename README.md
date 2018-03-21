# Communitybot-VPcontrol
Currently there is an issue with steemit community accounts, they can run over onto 100% VP and the community will then lose value instead of making money on a upvote. 
This Bot will watch your community account and initiate a self upvote on community account comment so that instead of hitting 100% your community account can continue to grow and help the community. 
This bot was built with the express purpose of controling the amount of times the @comedyopenmic account would hit 100%. Now the community gets to reap the benefits of a greater upvote instead.
Other people are free to use the code to help their communities grow.

Usage :
Create file "keys.py"
content: 
Posting_Key="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

within file comvoter.py
edit variables:
MaxVP = 97 # Maximum VP you are happy for account to reach
cutofftime = 518400 # Oldest time in seconds you are happy to upvote a comment

Account("comedyopenmic", s) # change all account names to your account

To Run: 

in terminal 

python3 comvoter.py



That's about it. 

I should probably clean it up a bit so I'll work on that.
