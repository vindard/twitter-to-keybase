import requests
import re, ast
import os, sys, shutil
from subprocess import call
import json, time

# Files
folders = [r'results', r'results/temp']
for f in folders:
    if not os.path.exists(f):
        os.makedirs(f)

# find the data file, assign to 'dataIn' variable
allFiles = []
filesToExtract = ['following.js', 'follower.js']
zipFound = False
for filename in os.listdir('data'):
    if is_zipfile(filename):
        zipFound = True
        with ZipFile(filename, 'r') as unzipped:
            for f in filesToExtract:                
                try:                
                    unzipped.extract(f)
                    allFiles.append(f)
                except KeyError:
                    pass
if not(zipFound):
    for filename in os.listdir('data'):
        if '.js' in filename:
            allFiles.append(filename)


# set the results file
parsedUsernames = 'results/temp/parsedUsernames.txt'
resultsOut = 'results/onKeybase.txt'
open(parsedUsernames, 'a').close() # makes file if it doesn't exist

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
def processedUsers():
    processedUserIDs = []
    lookupDict = {}
    with open(parsedUsernames, 'r') as p:
        try:
            processed = ast.literal_eval(p.read().replace('\n', ''))
        except SyntaxError:
            processed = []
    for userDict in processed:
        for k, v in userDict.items():
            processedUserIDs.append(k)
            lookupDict[k] = v
    return processedUserIDs, processed, lookupDict


def fetchUsername(allUserIDs):
    timeout = 0
    attempts = 10
    allUsernames = []
    count = len(allUserIDs)
    processedUserIDs, processed, lookupDict = processedUsers()
    pingMsg, fileMsg = "pinging Twitter...", "(from file) |"

    while len(allUserIDs) > 0:
        # logic for loop counter
        if timeout >= attempts:
            time.sleep(1)
            http_error = data.status_code
            print(f"Twitter endpoint exhausted. Please try again in 1 minute.")
            print(f"([HTTP {http_error} Code] for reference)\n")
            sys.exit(10)

        userid = allUserIDs.pop(0)

        # check processed file first for userid
        if userid in processedUserIDs:
            username = lookupDict[userid]
            allUsernames.append(username)
            print(f"{fileMsg} {len(allUsernames)} of {count}: @{lookupDict[userid]}")
            continue

        # ping Twitter if userid not found in processed file
        time.sleep(0.1)
        print(pingMsg)
        url = url_head + userid
        data = requests.get(url)
        try:
            username = re.findall("\(@(.*?)\) on Twitter", data.text.replace("\n", ""))[0]
            allUsernames.append(username)
            userDict = {userid: username}
            processed.append(userDict)
            print(end="\033[F")
            print(f"{pingMsg} {len(allUsernames)} of {count}: @{username}")

            with open(parsedUsernames, 'r+') as p:
                p.write(str(processed))

            timeout = 0
        except IndexError: # Twitter times out around every 100 lookups
            warn, bold, _end= '\033[93m', '\033[1m', '\033[0m'
            dots = [".  ", ".. ", "..."]

            if timeout == 0:
                print(f"{warn}{len(allUsernames)+1} of {count}: userID #{userid} failed{_end}")
            else:
                print(end="\033[F" * 4)

            timeout += 1
            allUserIDs.insert(0, userid)

            print(f"\nTwitter request limit temporarily exceeded.", \
                    f"Will try {bold}{attempts} attempts{_end} to regain connection.")
            print(f"(Attempt {warn}#{timeout} of {attempts}{_end}), please wait{dots[timeout%3]}\n")

    return allUsernames


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
    allUserIDs = []
    for i in dataIn:
        userid = i[list(i.keys())[0]]['accountId']
        if userid not in allUserIDs:
            allUserIDs.append(userid)

    return fetchUsername(allUserIDs)


def run():
    allUsernames = getTwitterUsernames() #replace this assignment if alternative Twitter list source
    usernamesOnKeybase = fetchKeybase(allUsernames)

    # Write usernames list to file
    usernamesJSON = json.dumps(usernamesOnKeybase, indent=2)
    with open(resultsOut, 'w') as results:
        results.write(f"usernames = {usernamesJSON}")
    b, _b = '\033[1m', '\033[0m'
    print(f"\n\nYOU HAVE {len(usernamesOnKeybase)} TWITTER USERS ON KEYBASE:\n{usernamesJSON[1:-3]}")
    print(f"\n*** Usernames on Keybase have been placed at {b}'{resultsOut}'{_b}. ***\n")


if __name__ == "__main__":
    run()
