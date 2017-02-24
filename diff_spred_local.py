#!/usr/bin/python

import os
import itertools
import pyxnat

# Which MR sessions for each subject haven't been uploaded to SPReD yet?

# 1. IDENTIFY MR SESSIONS IN LOCAL MR160 DIRECTORY

# find all MR Session subdirectories
MR160local_raw  = os.listdir('/micehome/mjoseph/data8/mrdata/MR160')

# read SiteCodeDict.txt into dictionary
siteCodeDict = {}
for line in open('siteCodeDict.txt'):
    siteCodeDict[line.split(':')[0].strip(' ')] = line.split(':')[1].strip(' \n')

# remove backups, withdrawn sessions, tests and QC scans
MR160local = []
for names in MR160local_raw:
    for codes in siteCodeDict:
        if names.startswith('MR160-' + siteCodeDict[codes]):    
            MR160local.append(names)

# 2. IDENTIFY MR SESSIONS ALREADY UPLOADED TO SPReD

# without supplying username or password, program asks user to enter in command line
spred = pyxnat.Interface(server='https://spred.braincode.ca/spred')

# apply constraints to retrieve only MR sessions from 'PND03_HSC' project
constraints = [('xnat:subjectData/PROJECT', '=', 'PND03_HSC')]

# retrieve json table with one MR session per row and the column MR session label (otherwise, retrieves accession #)
MR160spredJSON = spred.select('xnat:mrSessionData',['xnat:mrSessionData/XNAT_COL_MRSESSIONDATALABEL']).where(constraints)

# pyxnat has its own set of arguments to convert json to list of lists
MR160spredList = MR160spredJSON.as_list()

#unpack list and remove header
MR160spred = list(itertools.chain(*MR160spredList[1:]))

# convert MR160spred labeling to MR160local
MR160spredmod = []
for row in MR160spred:
    if len(row.split('_')) == 6:
        [Study, SiteCode, Subj, Visit, SessionNum, SessionType] = row.split('_')
        for sites in siteCodeDict:
            Site = siteCodeDict[SiteCode]
        sessionID = 'MR160-%s-%s-%s' % (Site, Subj, Visit)
    else: 
        [Study, SiteCode, Subj, Visit, SessionNum, SessionType, Deleted] = row.split('_')
        for sites in siteCodeDict:
            Site = siteCodeDict[SiteCode]   
        sessionID = 'MR160-%s-%s-%s-deleted' % (Site, Subj, Visit)
    MR160spredmod.append(sessionID)

# 3. FIND DIFFERENCE BETWEEN MR SESSIONS IN LOCAL MR160 DIRECTORY and SPReD

# Retrieves all MR sessions that haven't been uploaded yet
spredToDo = list(set(MR160local) - set(MR160spredmod))

# Retrieves all the deleted MR sessions from SPReD; but also found PND03_HBK_0446_02_SE01_MR
spredDeleted = list(set(MR160spredmod) - set(MR160local))

print "The following MR sessions haven't been uploaded to SPReD yet:"
for i in spredToDo:
    print i

print "The following MR sessions have been deleted from SPReD:"
for j in spredDeleted:
    print j
