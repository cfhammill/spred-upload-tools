#!/usr/bin/env python

"""
project
|__subject
   |__experiment
      |__scan
         |__DICOM
         |__RDA
         |__TWIX
         |__SNAPSHOTS

PND03_HBK_0004/PND03_HBK_0004_02_SE01_MR/13-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0004/PND03_HBK_0004_02_SE01_MR/13-MRS_GABA_Cere_met/DICOM
PND03_HBK_0090/PND03_HBK_0090_01_SE01_MR/14-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0090/PND03_HBK_0090_01_SE01_MR/14-MRS_GABA_Cere_met/DICOM
PND03_HBK_0116/PND03_HBK_0116_01_SE01_MR/5-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0116/PND03_HBK_0116_01_SE01_MR/5-MRS_GABA_Cere_met/DICOM
PND03_HBK_0136/PND03_HBK_0136_01_SE01_MR/15-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0136/PND03_HBK_0136_01_SE01_MR/15-MRS_GABA_Cere_met/DICOM
PND03_HBK_0137/PND03_HBK_0137_01_SE01_MR/13-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0137/PND03_HBK_0137_01_SE01_MR/13-MRS_GABA_Cere_met/DICOM
PND03_HBK_0145/PND03_HBK_0145_01_SE01_MR/13-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0145/PND03_HBK_0145_01_SE01_MR/13-MRS_GABA_Cere_met/DICOM
PND03_HBK_0165/PND03_HBK_0165_01_SE01_MR/13-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0165/PND03_HBK_0165_01_SE01_MR/13-MRS_GABA_Cere_met/DICOM
PND03_HBK_0167/PND03_HBK_0167_01_SE01_MR/13-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0167/PND03_HBK_0167_01_SE01_MR/13-MRS_GABA_Cere_met/DICOM
PND03_HBK_0180/PND03_HBK_0180_01_SE01_MR/37-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0180/PND03_HBK_0180_01_SE01_MR/37-MRS_GABA_Cere_met/DICOM
PND03_HBK_0182/PND03_HBK_0182_03_SE01_MR/18-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0182/PND03_HBK_0182_03_SE01_MR/18-MRS_GABA_Cere_met/DICOM
PND03_HBK_0182/PND03_HBK_0182_04_SE01_MR/7-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0182/PND03_HBK_0182_04_SE01_MR/7-MRS_GABA_Cere_met/DICOM
PND03_HBK_0184/PND03_HBK_0184_01_SE01_MR/16-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0184/PND03_HBK_0184_01_SE01_MR/16-MRS_GABA_Cere_met/DICOM
PND03_HBK_0189/PND03_HBK_0189_01_SE01_MR/14-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0189/PND03_HBK_0189_01_SE01_MR/14-MRS_GABA_Cere_met/DICOM
PND03_HBK_0194/PND03_HBK_0194_03_SE01_MR/15-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0194/PND03_HBK_0194_03_SE01_MR/15-MRS_GABA_Cere_met_1/TWIX
PND03_HBK_0194/PND03_HBK_0194_03_SE01_MR/15-MRS_GABA_Cere_met/DICOM
PND03_HBK_0195/PND03_HBK_0195_04_SE01_MR/13-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0195/PND03_HBK_0195_04_SE01_MR/13-MRS_GABA_Cere_met_1/TWIX
PND03_HBK_0195/PND03_HBK_0195_04_SE01_MR/13-MRS_GABA_Cere_met/DICOM
PND03_HBK_0198/PND03_HBK_0198_01_SE01_MR/20-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0198/PND03_HBK_0198_01_SE01_MR/20-MRS_GABA_Cere_met/DICOM
PND03_HBK_0222/PND03_HBK_0222_01_SE01_MR/13-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0222/PND03_HBK_0222_01_SE01_MR/13-MRS_GABA_Cere_met/DICOM
PND03_HBK_0224/PND03_HBK_0224_01_SE01_MR/4-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0224/PND03_HBK_0224_01_SE01_MR/4-MRS_GABA_Cere_met/DICOM
PND03_HBK_0232/PND03_HBK_0232_01_SE01_MR/15-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0232/PND03_HBK_0232_01_SE01_MR/15-MRS_GABA_Cere_met/DICOM
PND03_HBK_0234/PND03_HBK_0234_01_SE01_MR/16-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0234/PND03_HBK_0234_01_SE01_MR/16-MRS_GABA_Cere_met/DICOM
PND03_HBK_0235/PND03_HBK_0235_01_SE01_MR/15-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0235/PND03_HBK_0235_01_SE01_MR/15-MRS_GABA_Cere_met/DICOM
PND03_HBK_0239/PND03_HBK_0239_01_SE01_MR/16-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0239/PND03_HBK_0239_01_SE01_MR/16-MRS_GABA_Cere_met/DICOM
PND03_HBK_0242/PND03_HBK_0242_01_SE01_MR/14-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0242/PND03_HBK_0242_01_SE01_MR/14-MRS_GABA_Cere_met/DICOM
PND03_HBK_0247/PND03_HBK_0247_01_SE01_MR/14-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0247/PND03_HBK_0247_01_SE01_MR/14-MRS_GABA_Cere_met/DICOM
PND03_HBK_0248/PND03_HBK_0248_01_SE01_MR/17-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0248/PND03_HBK_0248_01_SE01_MR/17-MRS_GABA_Cere_met/DICOM
PND03_HBK_0249/PND03_HBK_0249_02_SE01_MR/13-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0249/PND03_HBK_0249_02_SE01_MR/13-MRS_GABA_Cere_met/DICOM
PND03_HBK_0253/PND03_HBK_0253_01_SE01_MR/14-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0253/PND03_HBK_0253_01_SE01_MR/14-MRS_GABA_Cere_met/DICOM
PND03_HBK_0261/PND03_HBK_0261_01_SE01_MR/13-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0261/PND03_HBK_0261_01_SE01_MR/13-MRS_GABA_Cere_met/DICOM
PND03_HBK_0265/PND03_HBK_0265_01_SE01_MR/13-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0265/PND03_HBK_0265_01_SE01_MR/13-MRS_GABA_Cere_met/DICOM
PND03_HBK_0273/PND03_HBK_0273_01_SE01_MR/5-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0273/PND03_HBK_0273_01_SE01_MR/5-MRS_GABA_Cere_met_1/TWIX
PND03_HBK_0273/PND03_HBK_0273_01_SE01_MR/5-MRS_GABA_Cere_met/DICOM
PND03_HBK_0280/PND03_HBK_0280_01_SE01_MR/13-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0280/PND03_HBK_0280_01_SE01_MR/13-MRS_GABA_Cere_met/DICOM
PND03_HBK_0281/PND03_HBK_0281_01_SE01_MR/13-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0281/PND03_HBK_0281_01_SE01_MR/13-MRS_GABA_Cere_met/DICOM
PND03_HBK_0285/PND03_HBK_0285_01_SE01_MR/10-MRS_GABA_Cere_met_1/RDA
PND03_HBK_0285/PND03_HBK_0285_01_SE01_MR/10-MRS_GABA_Cere_met_1/TWIX
PND03_HBK_0285/PND03_HBK_0285_01_SE01_MR/10-MRS_GABA_Cere_met/DICOM


"""

import requests
import base64
from base64 import b64encode
import pyxnat
import os
import sys
from urllib2 import Request, urlopen, URLError
import base64
import json

user = raw_input("Username: ")
passwd = getpass("Password for " + user + ": ")
url = "https://spreddev.braincode.ca/spred/data/archive"

url_project = "https://spreddev.braincode.ca/spred/data/archive/projects"
#url_subject = "https://spreddev.braincode.ca/spred/data/archive/subjects"
#url_session = "https://spreddev.braincode.ca/spred/data/archive/experiments"
#url_scan = "https://spreddev.braincode.ca/spred/data/archive/scans"
#url_resource = "https://spreddev.braincode.ca/spred/data/archive/resources"
#url_project_resource = "https://spreddev.braincode.ca/spred/data/archive/

usrPass = "%s:%s" % (user, passwd)
b64Val = base64.b64encode(usrPass.encode()).decode()

url = "https://spred.braincode.ca/spred/data/archive/experiments?format=json&columns=xnat:mrSessionData/label&project=PND03_HSC,PND03_HSC_B"

response = requests.get(url, headers={"Authorization": "Basic %s" % b64Val})
result = response.json()
result_body = result['ResultSet']['Result']
MR160spred = []
for item in result_body:
    label = item['xnat:mrsessiondata/label']
    MR160spred.append(label)








file = open('', 'rb').read()
requests.post(url,, data="myDataToPost")

url = 'https://spreddev.braincode.ca/spred'

# base64 authentication of username and password
usrPass = 'username:password'
b64Val = base64.b64encode(usrPass)
r = requests.post(url, 
    headers={"Authorization": "Basic %s" % b64Val,
    "Content_Type", "application/zip",
    "Content-Length", '%d' % length
    },
    data=payload)

"Authorization", "Basic %s" % base64string
"Content-Type", "application/zip"
"Content-Length", '%d' % length

length = os.path.getsize(s)
data = open(s, "rb")
req = urllib2.Request(url,data)
base64string = base64.encodestring('%s:%s' % (op.user, pw)).replace('\n', '')

response = urllib2.urlopen(req)



request = Request('https://spred.braincode.ca/spred')
try:
    response = urlopen(request)
    kittens = response.read()
    print kittens[559:1000]
except URLError, e:
    print 'No kittez. Got an error code:', e


# Obtain a list of projects present at the site:
request = urllib2.Request(site + "/REST/projects?format=json") 
base64string = base64.encodestring('%s:%s' % (user, password)).replace('\n', '') request.add_header("Authorization", "Basic %s" % base64string)
response = urllib2.urlopen(request) 
html = response.read() 
data = json.loads(html) projectsIt = data['ResultSet']['Result'] #




request = urllib2.Request(url, data) 

urllib2.Request(url,data)



mrs_dir = '/Users/Michael/Desktop/MRS_test'

# without supplying username or password, program asks user to enter in command line
xnat = pyxnat.Interface(server='https://spreddev.braincode.ca/spred')

project = xnat.select.project('PND03_HSC_test')
if not project.exists():
    raise Exception('ERROR - Project does not exist')
else:
    subject_dirs = ['{0}/{1}'.format(mrs_dir, i) for i in os.listdir(mrs_dir)]
    for subject_dir in subject_dirs:
        subject = project.subject(subject_dir.split('/')[-1])
        if not subject.exists():
            subject.create()
        else:    
            experiment_dirs = ['{0}/{1}'.format(subject_dir, j) for j in os.listdir(subject_dir)]
            for experiment_dir in experiment_dirs:
                experiment = subject.experiment(experiment_dir.split('/')[-1])
                if not experiment.exists():
                    experiment.create(experiments='xnat:mrSessionData')
                scan_dirs = ['{0}/{1}'.format(experiment_dir, j) for j in os.listdir(experiment_dir)]
                for scan_dir in scan_dirs:
                    scan = experiment.scan(scan_dir.split('/')[-1].split('-')[0])
                    if not scan.exists():
                        scan.create(scans='xnat:mrScanData') 
                        scan.attrs.mset({
                            'xnat:mrScanData/type' : scan_dir.split('/')[-1].lstrip('0123456789-'),
                            'xnat:mrScanData/quality' : 'unknown',
                            'xnat:mrScanData/series_description' : scan_dir.split('/')[-1].lstrip('0123456789-'),
                            'xnat:mrScanData/parameters/imageType' : '',
                            'xnat:mrScanData/fieldStrength' : '',
                            'xnat:mrScanData/parameters/voxelRes/x' : '',
                            'xnat:mrScanData/parameters/voxelRes/y' : '',
                            'xnat:mrScanData/parameters/voxelRes/z' : '',
                            # FOV
                            'xnat:mrScanData/parameters/tr' : '',
                            'xnat:mrScanData/parameters/te' : '',
                            # Flip
                            'xnat:mrScanData/parameters/sequence' : '',
                            })
                    scans_to_upload = os.listdir(scan_dir)
                    for scans_upload in scans_to_upload:
                        if scans_upload == 'DICOM':
                            dcm_dir = os.path.join(scan_dir, 'DICOM')
                            dcm_resource = scan.resource('DICOM')
                            dcm_resource.put_dir(dcm_dir)
                        elif scans_upload == 'RDA':
                            rda_resource = scan.resource('RDA')
                            rda_resource.put_dir(os.path.join(scan_dir, 'RDA'))
                        elif scans_upload == 'TWIX':
                            twix_resource = scan.resource('TWIX')
                            twix_resource.put_dir(os.path.join(scan_dir, 'TWIX'))

