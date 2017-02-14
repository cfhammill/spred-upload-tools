#!/usr/bin/python

import os
import itertools
import pyxnat

# Which MR sessions for each subject haven't been uploaded to SPReD yet?

# 1. IDENTIFY MR SESSIONS IN LOCAL MR160 DIRECTORY

# find all MR Session subdirectories
MR160local_raw  = os.listdir('/micehome/mjoseph/data8/mrdata/MR160')

# remove backups, withdrawn sessions, tests and QC scans
MR160local = []
Tags = ('MR160-088', 'MR160-105', 'MR160-113', 'MR160-114')
for names in MR160local_raw:
    if names.startswith(Tags):    
        MR160local.append(names)

# 2. IDENTIFY MR SESSIONS ALREADY UPLOADED TO SPReD

spred = pyxnat.Interface(server='https://spred.braincode.ca/spred')

MR160spredJSON = spred.select('xnat:mrSessionData',['xnat:mrSessionData/XNAT_COL_MRSESSIONDATALABEL']).all()
# outputs as a json table

# pyxnat has its own set of arguments to convert json to list of lists
MR160spredList = MR160spredJSON.as_list()

#unpack list and remove header
MR160spred = list(itertools.chain(*newSessionLabel[1:]))

# convert MR160spred labeling to MR160local
MR160spredmod = []
for row in MR160spred:
    if len(row.split('_')) == 6:
        [Study, SiteCode, Subj, Visit, SessionNum, SessionType] = row.split('_')
        if SiteCode=='HSC':
            Site = '088'
        else:
            Site = '105'
        sessionID = 'MR160-%s-%s-%s' % (Site, Subj, Visit)
    else: 
        [Study, Site, Subj, Visit, SessionNum, SessionType, Deleted] = row.split('_')
        if SiteCode=='HSC':
            Site = '088'
        else:
            Site = '105'        
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
