import requests
import re, ast
import os, sys, shutil
from subprocess import call

# Files
folders = [r'results', r'results/temp']
for f in folders:
    if not os.path.exists(f):
        os.makedirs(f)

# find the data file, assign to 'dataIn' variable
allFiles = []
for filename in os.listdir('data'):
    if '.js' in filename:
        allFiles.append(filename)


# set the results file
resultsOut = 'results/onKeybase.txt'

# set Twitter lookup URL
url_head = 'https://twitter.com/intent/user?user_id='


# get the Twitter userID list data
def getData(readFile):
    writeFile = 'results/temp/data.txt'
    with open(readFile, 'r') as r, open(writeFile, 'w') as w:
        for i, line in enumerate(r):
            if i == 0:
                trunc = re.findall('= (.*)', line)[0]
                w.write(trunc + '\n')
            else:
                w.write(line)
    with open(writeFile, 'r') as w:
        return ast.literal_eval(w.read())


dataIn = []
try:
    for f in allFiles:
        datafile = 'data/' + f
        dataIn.extend(getData(datafile))
except NameError:
    print("Error: Data file is missing from 'data/' directory.")
    sys.exit(1)



# Processing functions
def runMsg(username, firstRun, allUsernames, skipped):
    if firstRun:
        print(f"{len(allUsernames)} of {len(dataIn)}: @{username}")
    else:
        print(f"{len(allUsernames)} of {len(dataIn)}: @{username} | in skipped #{len(skipped)}")


def fetchUsername(userid, firstRun, allUsernames, skipped):
    url = url_head + userid
    data = requests.get(url)
    try:
        username = re.findall("\(@(.*?)\) on Twitter", data.text.replace("\n", ""))[0]
        if username not in allUsernames:
            allUsernames.append(username)
            runMsg(username, firstRun, allUsernames, skipped)
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
    open(scraped, 'w').close()  # creates/clears file
    for i, foll in enumerate(my_followers):
        callable = foll + "@twitter"
        print(f"Retrieving {i+1} of {len(my_followers)}: {callable}...")
        with open(scraped, 'a') as s:
            call(["keybase", "id", callable], stdout=s, stderr=s)

    # Filter out names not found
    open(filtered, 'w').close()  # creates/clears file
    check = 'No resolution found'
    with open(scraped, 'r') as s:
        for line in s:
            if check not in line:
                with open(filtered, 'a') as f:
                    f.write(line)

    # Extract usernames as list from filtered data
    with open(filtered, 'r') as f:
        data = f.read().replace('\n', '')
    usernamesOnKeybase = re.findall("Identifying \[1m(.*?)", data)

    # Clean up temp files
    shutil.rmtree("results/temp")

    return usernamesOnKeybase


def getTwitterUsernames():
    allUsernames = []
    skipped = []

    firstRun = True
    for i in dataIn:
        userid = i[list(i.keys())[0]]['accountId']
        fetchUsername(userid, firstRun, allUsernames, skipped)

    firstRun = False
    while len(skipped) > 0:
        userid = skipped.pop()
        fetchUsername(userid, firstRun, allUsernames, skipped)

    return allUsernames


def run():
    allUsernames = getTwitterUsernames() #replace this assignment if alternative Twitter list source
    usernamesOnKeybase = fetchKeybase(allUsernames)

    # Write usernames list to file
    with open(resultsOut, 'w') as results:
        results.write("usernames = " + str(usernamesOnKeybase))
    print(f"Usernames on Keybase have been filtered and placed at '{resultsOut}'")


if __name__ == "__main__":
    run()
