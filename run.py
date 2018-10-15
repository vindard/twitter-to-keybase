import requests
import re, ast
import os, shutil
from subprocess import call

# Files
results = r'results'
if not os.path.exists(results):
    os.makedirs(results)
temp = r'results/temp'
if not os.path.exists(temp):
    os.makedirs(temp)
dataOut = 'results/twitterListUsernames.py'
resultsOut = 'results/onKeybase.txt'

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

allUsernames = []
skipped = []

def runMsg(username, firstRun):
    if firstRun:
        print(f"{len(allUsernames)} of {len(dataIn)}: @{username}")
    else:
        print(f"{len(allUsernames)} of {len(dataIn)}: @{username} | in skipped #{len(skipped)}")

def fetchUsername(userid, firstRun):
    url = url_head + userid
    data = requests.get(url)
    try:
        username = re.findall("\(@(.*?)\) on Twitter", data.text.replace("\n",""))[0]
        allUsernames.append(username)
        runMsg(username, firstRun)
    except IndexError:
        skipped.append(userid)
        print(f"{len(skipped)} in skipped: {userid} | twitter timeout, please wait...")
        # Twitter pings start returning 404's every 100 lookups,
        # so this is to store failed attempts during timeout
        # and retry at the end of the cycle.

def fetchKeybase(my_followers):
    scraped = 'results/temp/scrape.txt'
    filtered = 'results/temp/filtered.txt'

    # Scrape twitter usernames against Keybase
    open(scraped, 'w').close() # creates/clears file
    for i, foll in enumerate(my_followers):
        callable = foll + "@twitter"
        print(f"Retrieving {i+1} of {len(my_followers)}: {callable}...")
        with open(scraped, 'a') as s:
            call(["keybase","id",callable], stdout=s, stderr=s)

    # Filter out names not found
    open(filtered, 'w').close() # creates/clears file
    check = 'No resolution found'
    with open(scraped, 'r') as s:
        for line in s:
            if check not in line:
                with open(filtered, 'a') as f:
                    f.write(line)

    # Extract usernames as list from filtered data
    with open(filtered, 'r') as f:
        data = f.read().replace('\n', '')
    usernames = re.findall("Identifying \[1m(.*?)", data)

    # Clean up temp files
    shutil.rmtree("results/temp")

    return usernames


def run():
    # To do: clean up this logic and make allUsernames/skipped
    # not global variables
    firstRun = True
    for i in dataIn:
        userid = i['following']['accountId']
        fetchUsername(userid, firstRun)
    firstRun = False

    while len(skipped)>0:
        userid = skipped.pop()
        fetchUsername(userid, firstRun)

    usernames = fetchKeybase(allUsernames)
    # Write usernames list to file
    with open(resultsOut, 'w') as results:
        results.write("usernames = " + str(usernames))
    print(f"Usernames on Keybase have been filtered and placed at '{resultsOut}'")

if __name__ == "__main__":
    run()
