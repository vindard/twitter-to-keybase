import requests
import re, os
import json
from data.following import following as following

# Files
results = r'results' 
if not os.path.exists(results):
    os.makedirs(results)
dataOut = 'results/twitterListUsernames.py'

# get the data
url_head = 'https://twitter.com/intent/user?user_id='

my_following = []
not_found = []

def runMsg(username, firstRun):
    if firstRun:
        print(f"{len(my_following)} of {len(following)}: @{username}")
    else:
        print(f"{len(my_following)} of {len(following)}: @{username} | in skipped #{len(not_found)}")

def fetchUsername():
    url = url_head + id
    data = requests.get(url)
    try:
        username = re.findall("\(@(.*?)\) on Twitter", data.text.replace("\n",""))[0]
        my_following.append(username)
        runMsg(username, firstRun)
    except IndexError:
        not_found.append(id)
        print(f"{len(not_found)} in skipped: {id} | twitter timeout, please wait...")
        # Twitter pings start returning 404's every 100 lookups,
        # so this is to store failed attempts during timeout 
        # and retry at the end of the cycle.


firstRun = True
for i in following:
    id = i['following']['accountId']
    fetchUsername()    
firstRun = False

while len(not_found)>0:
    id = not_found.pop()    
    fetchUsername()

myfile = open(dataOut, 'w')
myfile.write("usernames = "+str(my_following))
myfile.close()