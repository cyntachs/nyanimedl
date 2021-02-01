#!/usr/bin/env python3
# =========================
#  Nyanime Torrent Monitor
# =========================
# 
# Monitors nyaa.si rss feeds (user provided) for new episodes
# and downloads the .torrent metainfo files
# 
# *requires [feedparser] and [wget] modules*
# *technically just a rss feed link downloader*
# -----------------------
# 


# =========
#  Imports
# =========

# Import sys
import sys

# Check version before continuing
if (sys.version_info < (3,8,5)):
    print('This application requires Python 3.8.5 or greater')

# Import other dependencies
import string
import os.path
import uuid
import datetime
import time
import sched

# Try import feedparser
try: import feedparser
except ImportError:
    print('This application requires the feedparser module to run')
    sys.exit(-10)

# Try import wget
try: import wget
except ImportError:
    print('This application requires the wget module to run')
    sys.exit(-11)


# ========
#  Config
# ========

# Check interval (in seconds). Default: 3600
CheckInterval = 3600
# Torrent file donwload location
DownloadLocation = './Downloads/'
# Feeds file location
FeedsFileLocation = './Feeds.txt'


# ===========
#  Functions
# ===========

# log(str)
# log function that outputs to a log file and stdout
def log(str):
    currtime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    logstr = '[' + currtime + '] ' + str
    print(logstr)
    outfile = open('logs.txt', 'a')
    outfile.write(logstr + '\n')
    outfile.close()

# [List] getFeeds()
# load feed urls from file
def getFeeds():
    # load file with feeds
    inputfile = open(FeedsFileLocation, 'r')

    # list of feeds
    feeds = []

    for line in inputfile:
        line = line.strip() # remove trailing spaces
        if line and line[0] != '`': # remove empty lines and line comments
            if '`' in line:
                line = line.split('`')[0].strip() # remove inline comments
            feeds.append(line) # append to list
    
    inputfile.close() # close file
    return feeds

# [str] getId(url)
# returns a string uuid of the url
def getId(url):
    return str(uuid.uuid5(uuid.NAMESPACE_URL,url))

# [list] loadHistory(url)
# returns a list with publication history of provided url from file
def loadHistory(url):
    filename = './history/' + getId(url) + '.hlt'
    if os.path.isfile(filename): # if file exists
        inputfile = open(filename, 'r')
        hist = []
        for line in inputfile:
            hist.append(line.strip())
        inputfile.close()
        return hist
    return []

# writeHistory(url,dat)
# appends publication date to history file of url
def writeHistory(url, dat):
    outfile = open('./history/' + getId(url) + '.hlt', 'a')
    outfile.write(dat + '\n')
    outfile.close()

# [bool] checkHistory(url,dat)
# check if a publication date is in history
def checkHistory(url, dat):
    hist = loadHistory(url)
    if str(dat) in hist:
        return True
    return False

# checkUpdate()
# checks for update and downloads new files
def checkForUpdates():
    #log('Checking for updates...') # spams log too much
    # load feed urls
    feeds = getFeeds()

    # parse feeds
    for fd in feeds:
        pfeed = feedparser.parse(fd)
        
        newcount = 0
        # check for new updates
        for entry in pfeed.entries:
            date = entry.published
            # check if entry is new
            if not checkHistory(fd, date):
                # download torrent file
                wget.download(entry.link, DownloadLocation)
                # write to history
                writeHistory(fd, date)
                # increment count
                newcount = newcount + 1
        if (newcount > 0):
            log(str(newcount) + ' new updates  -  ##(' + pfeed.feed.title + ')##')

# main()
# main function that runs the check loop
def main():
    log('NyanimeDL running...')

    checkForUpdates()

    # create scheduled interval event
    sch = sched.scheduler(time.time, time.sleep)

    # scheduled loop function
    def runloop(s):
        checkForUpdates()
        sch.enter(CheckInterval, 1, runloop, (s,))
    
    # start scheduled interval loop
    sch.enter(CheckInterval, 1, runloop, (sch,))
    sch.run()


# run main()
main()