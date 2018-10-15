# Purpose

This simple script is meant to take in a list of Twitter users and then check if they are registered on keybase.io with their Twitter usernames. It runs in a way that does not require either of the Twitter or Keybase APIs. 

The Twitter usernames are resolved from the userid's returned by Twitter using the "intent" endpoint for usernames that can be found at:
`https://twitter.com/intent/user?user_id=[userid]`

The Keybase comparisons are done by calling `$ keybase id [username]@twitter` from the command line for each user and parsing through the results returned.

## Pre-requisites

#### Keybase
Keybase needs to be [installed locally](https://keybase.io/download) since the script makes use of a keybase command line call to work. 

#### Twitter list of users
Your respective Twitter list can be gotten by ["requesting your data"](https://help.twitter.com/en/managing-your-account/how-to-download-your-twitter-archive) under your Twitter settings. Specifically, the `followers` and `following.js` files are what this script is designed to work with from the bundle that Twitter returns.

## To run
To run, simply place your Twitter user file into the `data` folder and then run `run.py` using:
`$ python3 run.py`
