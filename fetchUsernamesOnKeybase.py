import re, os, shutil
from subprocess import call
from results.twitterListUsernames import usernames as my_followers

temp = r'results/temp' 
if not os.path.exists(temp):
    os.makedirs(temp)
scraped = 'results/temp/scrape.txt'
filtered = 'results/temp/filtered.txt'
onKeybase = 'results/onKeybase.txt'
open(scraped, 'w').close() # creates/clears file
open(filtered, 'w').close() # creates/clears file

# Scrape twitter usernames against Keybase
for i, foll in enumerate(my_followers):
    callable = foll + "@twitter"
    print(f"Retrieving {i+1} of {len(my_followers)}: {callable}...")
    with open(scraped, 'a') as s:
        call(["keybase","id",callable], stdout=s, stderr=s)

# Filter out names not found
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

# Write usernames list to file
with open(onKeybase, 'w') as results:
    results.write("usernames = "+str(usernames))
print(f"Usernames on Keybase have been filtered and placed at '{onKeybase}'")

# Clean up temp files
shutil.rmtree("results/temp")