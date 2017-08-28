#!/usr/bin/env python

"""
Description: Takes a zipped MR session and uploads DICOM and 
             non-DICOM files contained in it to SPReD.
             Multiple sessions can be uploaded by repeating the 
             --sessions (-s) argument

Caveat:      If subject or session does not exist on SPReD yet,
             zipped session must contain DICOMs. If only non-DICOMs
             present, none of them will get uploaded.

"""

import os
import sys
import argparse
import logging
from getpass import getpass
import requests
import zipfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# create a file handler
handler = logging.FileHandler('uploader.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)


def main():
    parser = argparse.ArgumentParser(
        prog = "uploader.py",
        description = __doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    required = parser.add_argument_group('required arguments')
    required.add_argument("-u", "--user", 
        help="help: SPReD username")
    required.add_argument("-p", "--project", 
        help="help: SPReD Project ID")
    required.add_argument("-s", "--sessions", action="append", default=[], 
        help="help: zipped MR session data")

    args = parser.parse_args()

    user = args.user
    project = args.project
    sessions = args.sessions
  
    server = "https://spred.braincode.ca/spred"

    passwd = getpass("Password for " + user + ": ")
    usrPass = (user, passwd)

    UPLOAD_URL = "{server}/data/services/import?" \
                 "dest=/archive/projects/{project}" \
                 "&overwrite=append&inbody=true"

    CREATE_URL = "{server}/data/archive/projects/{project}/subjects/{subject}" \
                 "/experiments/{session}/scans/{scan}"

    ATTACH_URL = "{server}/data/archive/projects/{project}/subjects/{subject}" \
                 "/experiments/{session}/scans/{scan}/resources/{resource}/files/{filename}?" \
                 "inbody=true"
    
    for session in sessions:
        upload_url = UPLOAD_URL.format(server=server, project=project)
        logger.info("Starting to upload contents of %s to project %s on SPReD ..." % (session, project))
        logger.info("Uploading DICOMs ...")
        logger.info("The upload URL is prepared as:\n\t%s" % upload_url)  
        
        response = requests.post(UPLOAD_URL.format(server=server, project=project),
                                 auth=usrPass,
                                 headers={"Content-Type" : "application/zip"},
                                 data=open(session, "rb"))

        status = response.status_code
        # returns a tuple of status code meanings
        # the first value in the tuple is the conventional code key
        status_meaning = requests.status_codes._codes[status][0]
        
        if status == 200:
            logger.info("Successfully uploaded all DICOM scans")
        else:
            logger.info("[%s] : %s Failed to upload DICOM scans" % (status, status_meaning)) 

        logger.info("Checking for any non-DICOMs ...")
        zf = zipfile.ZipFile(session)
        files = zf.namelist()
        files.sort()

        # filter out all directories, keeping only files
        nondicoms = list(filter(lambda x: not x.endswith('/'), files))
        # filter out all DICOMs (would already be uploaded)
        nondicoms = list(filter(lambda x: not x.lower().endswith(('.dcm','.ima')), nondicoms))
        # in case on macOS, remove .DS_Store files
        nondicoms = list(filter(lambda x: not x.endswith('.DS_Store'), nondicoms))

        # if nondicoms is empty, continue to next iteration of loop
        if not nondicoms:
            logger.info("No non-DICOMs found")
            continue
    
        else:
            logger.info("Uploading non-DICOMs ...")
            # before posting nondicoms, we need to create urls for new scans
            # returns 404 status code otherwise
            for f in nondicoms:
                (subject, session, scan_raw, resource, filename) = f.split('/')
                (scan, scantype) = scan_raw.split('-',1)
                scan = scan.lstrip("0")
                scan_params = {'xsiType' : 'xnat:mrScanData',
                               'xnat:mrScanData/type' : '%s' % scantype,
                               'xnat:mrScanData/series_description' : '%s' % scantype,
                               'xnat:mrScanData/quality' : 'unknown'}
                logger.info("Checking if scan %s-%s already created ..." % (scan, scantype))
                response = requests.get(CREATE_URL.format(server=server, project=project, subject=subject, session=session, scan=scan))
                status = response.status_code
                status_meaning = requests.status_codes._codes[status][0]
                if not status == 200:
                    logger.info("Scan %s-%s does not exist yet. Creating now ..." % (scan, scantype))
                    response = requests.put(CREATE_URL.format(server=server, project=project, subject=subject, session=session, scan=scan),
                                            params=scan_params,
                                            auth=usrPass)          
                    status = response.status_code
                    status_meaning = requests.status_codes._codes[status][0]
                    if status == 200:
                        logger.info("Successfully created scan %s-%s" % (scan, scantype))
                    else:
                        logger.info("[%s] : %s Failed to create scan %s-%s" % (status, status_meaning, scan, scantype))                       
                response = requests.post(ATTACH_URL.format(server=server, project=project, subject=subject, session=session, scan=scan, resource=resource, filename=filename),
                                         auth=usrPass,
                                         data=zf.open(f).read())
                status = response.status_code
                status_meaning = requests.status_codes._codes[status][0]                
                if status == 200:
                    logger.info("Successfully uploaded scan %s-%s" % (scan, scantype))
                else:
                   logger.info("[%s] : %s Failed to upload scan %s-%s" % (status, status_meaning, scan, scantype))   

if __name__ == '__main__':
    main()

