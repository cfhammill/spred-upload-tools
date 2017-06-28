#!/usr/bin/python

"""
@author: michael joseph
Description:
-------------
Usage: takes local MR session directory as input
       appends MR sessions to list, excluding backups, withdrawn sessions, tests and QC directories
       using XNAT REST API, retrieves json of MR sessions uploaded to SPReD
       currently configured only for MR160/PND03 data
Example usage: ./diff_spred_local.py /micehome/mjoseph/data8/mrdata/MR160
-------------
"""

import os
import re
from getpass import getpass
import requests
import base64

local_src_dir = '/micehome/mjoseph/data8/mrdata/MR160'

def diff_spred_local(local_src_dir):
    MR160local = []
    for session in os.walk(local_src_dir).next()[1]:
        if os.path.isdir(os.path.join(local_src_dir, session)) == True:
            MR160local.append(session)

    MR160local = filter(lambda x: re.match('MR160-\d+-\d+-\d+$', x) is not None, MR160local)

    # identify MR sessions already uploaded to SPReD

    user = raw_input("Username: ")
    passwd = getpass("Password for " + user + ": ")
    usrPass = "%s:%s" % (user, passwd)
    b64Val = base64.b64encode(usrPass.encode()).decode()

    print("Input the desired projects. If entering multiple projects, use commas between them without spaces.")
    projects = raw_input("Projects on SPReD: ")

    url = "https://spred.braincode.ca/spred/data/archive/experiments?format=json&columns=xnat:mrSessionData/label&project=%s" % (projects)

    response = requests.get(url, headers={"Authorization": "Basic %s" % b64Val})
    result = response.json()
    result_body = result['ResultSet']['Result']
    MR160spred = []
    for item in result_body:
        label = item['xnat:mrsessiondata/label']
        MR160spred.append(label)

    # convert labeling style of MR160spred to MR160local

    # read SiteCodeDict.txt into dictionary
    siteCodeDict = {}
    for line in open('siteCodeDict.txt'):
        siteCodeDict[line.split(':')[0].strip(' ')] = line.split(':')[1].strip(' \n')

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

    # find difference between MR sessions in local directory and SPReD

    # Retrieves all MR sessions that haven't been uploaded yet (82 MR sessions as of May 9, 2017)
    spredToDo = list(set(MR160local) - set(MR160spredmod))

    return spredToDo