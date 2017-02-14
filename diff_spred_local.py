#!/usr/bin/python

import os
import csv
import json
import itertools
import pyxnat

# Which MR sessions for each subject haven't been uploaded to SPReD yet?

# 1. CREATE VARIABLE OF MR SESSIONS IN LOCAL MR160 DIRECTORY

# Find all MR Session subdirectories
sessions_Raw = os.listdir('/micehome/mjoseph/data8/mrdata/MR160')
sessions = []
Tags = ('MR160-088', 'MR160-105', 'MR160-113', 'MR160-114')
for names in sessions_Raw:
    if names.startswith(Tags):    
        sessions.append(names)

# Create empty lists of each variable of interest to build
MR160local = []
for row in sessions:
    [Study, Site, Subj, Visit] = row.split('-')
    if Site=='088':
        SiteCode = 'HSC'
    else:
        SiteCode = 'HBK'

    subjectID = 'PND03_%s_%s' % (SiteCode,Subj)
        
    sessionSuffix = '%s_SE01_MR' % (Visit)
    sessionID = '%s_%s' % (subjectID, sessionSuffix)
    MR160local.append(sessionID)

# 2. CREATE VARIABLE OF MR SESSIONS ALREADY UPLOADED TO SPReD

spred_url = 'https://spred.braincode.ca/spred'

credentials = {}
with open('/micehome/mjoseph/Documents/Code/credentials.txt', 'r') as f:
    for line in f:
        user, pwd = line.strip().split(':')
        credentials[user] = pwd 

spred = pyxnat.Interface(server=spred_url, user=user, password=pwd)

session_label = spred.select('xnat:mrSessionData',['xnat:mrSessionData/XNAT_COL_MRSESSIONDATALABEL']).all()
# outputs as a json table

# convert to list
newSessionLabel = session_label.as_list()

#unpack list and remove header
MR160spred = list(itertools.chain(*newSessionLabel[1:]))

# 3. FIND DIFFERENCE BETWEEN MR SESSIONS IN LOCAL MR160 DIRECTORY and SPReD

# Retrieves all MR sessions that haven't been uploaded yet
spredToDo = list(set(MR160local) - set(MR160spred))

# Retrieves all the deleted MR sessions from SPReD; but also found PND03_HBK_0446_02_SE01_MR
list(set(MR160spred) - set(MR160local))

# instead of converting spredToDo back to original form, convert pyxnat to directory structure
