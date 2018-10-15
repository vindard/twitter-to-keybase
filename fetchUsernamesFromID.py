import requests
import re, os, ast

# Files
results = r'results' 
if not os.path.exists(results):
    os.makedirs(results)
temp = r'results/temp'
if not os.path.exists(temp):
    os.makedirs(temp)
dataOut = 'results/twitterListUsernames.py'

# get the data
url_head = 'https://twitter.com/intent/user?user_id='

def getData(readFile):
    writeFile = 'results/temp/data.txt'
    with open(readFile, 'r') as r, open(writeFile, 'w') as w:
        for i, line in enumerate(r):
            if i == 0:
                trunc = re.findall('= (.*)', line)[0]
                w.write(trunc+'\n')
            else:
                w.write(line)
    with open(writeFile, 'r') as w:
        return ast.literal_eval(w.read())

# find the data file, assign to 'dataIn' variable
for filename in os.listdir('data'):
    if '.js' in filename:
        datafile = 'data/' + filename
        break
dataIn = getData(datafile)

usernames = []
skipped = []

def runMsg(username, firstRun):
    if firstRun:
        print(f"{len(usernames)} of {len(dataIn)}: @{username}")
    else:
        print(f"{len(usernames)} of {len(dataIn)}: @{username} | in skipped #{len(skipped)}")

def fetchUsername(userid, firstRun):
    url = url_head + userid
    data = requests.get(url)
    try:
        username = re.findall("\(@(.*?)\) on Twitter", data.text.replace("\n",""))[0]
        usernames.append(username)
        runMsg(username, firstRun)
    except IndexError:
        skipped.append(userid)
        print(f"{len(skipped)} in skipped: {userid} | twitter timeout, please wait...")
        # Twitter pings start returning 404's every 100 lookups,
        # so this is to store failed attempts during timeout 
        # and retry at the end of the cycle.


def run():
    firstRun = True
    for i in dataIn:
        userid = i['following']['accountId']
        fetchUsername(userid, firstRun)    
    firstRun = False

    while len(skipped)>0:
        userid = skipped.pop()
        fetchUsername(userid, firstRun)

    myfile = open(dataOut, 'w')
    myfile.write("usernames = "+str(usernames))
    myfile.close()


if __name__ == "__main__":
    run()