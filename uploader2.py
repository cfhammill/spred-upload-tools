#!/usr/bin/python

import requests
import base64
import json
from getpass import getpass

user = raw_input("Username: ")
passwd = getpass("Password for " + user + ": ")
usrPass = "%s:%s" % (user, passwd)
b64Val = base64.b64encode(usrPass.encode()).decode()

CREATE_URL = "{server}/REST/projects/{project}/subjects/{subject}"

UPLOAD_URL = "{server}/data/services/import?" \
             "project={project}&subject={subject}&session={session}" \
             "&overwrite=delete&prearchive=false&inbody=true"

ATTACH_URL = "{server}/data/archive/projects/{project}/subjects/{subject}" \
             "/experiments/{session}/files/{filename}?" \
             "inbody=true"

subject = scanid
session = scanid
auth = (username, password)
url_params = { 'server'  : 'https://spreddev.braincode.ca/spred',
               'project' : 'PND03_HSC_test',
               'subject' : subject,
               'session' : session }


server = 'https://spred.braincode.ca/spred'
project = 'PND03_HSC'
subject = ''
session = ''
filename = ''


url = "https://spred.braincode.ca/spred/data/archive"

# Create the subject
# ** denotes kwargs, formatting values from dictionary
# * denotes args, formatting values from input arguments
r = requests.put(CREATE_URL.format(**url_params), auth=auth)

# Upload dicom stuff
r = requests.post(UPLOAD_URL.format(**url_params),
        auth=auth,
        headers={'Content-Type' : 'application/zip'},
        data=open(archive))

# Upload non-dicom stuff
zf = zipfile.Zipfile(archive)
files = zf.namelist()
files = filter(lambda f: not f.endswith('/'), files)
files = filter(lambda f: not is_named_like_a_dicom(f), files)
files = filter(lambda f: not is_dicom(io.BytesIO(zf.read(f))), files)

for f in files:
    uploadname = urllib.quote(f)
    r = rqeuests.post(ATTACH_URL.format(filename=uploadname, **url_params), data=zf.read(f), auth=auth)
    r.raise_for_status()



response = requests.get(url, headers={"Authorization": "Basic %s" % b64Val})
result = response.json()
result_body = result['ResultSet']['Result']
MR160spred = []
for item in result_body:
    label = item['xnat:mrsessiondata/label']
    MR160spred.append(label)

URL = 'https://spred.braincode.ca/spred/data/services/import'

url = '{0}?dest=/archive/projects/{1}&overwrite=append&inbody=true"'.format(URL, op.project)

print 'The upload URL is prepared as:\n\t%s' % url

for s in op.subject:
    length = os.path.getsize(s)
    data = open(s, "rb")
    req = urllib2.Request(url,data)
    base64string = base64.encodestring('%s:%s' % (op.user, pw)).replace('\n', '')
    req.add_header("Authorization", "Basic %s" % base64string)
    req.add_header("Content-Type", "application/zip")
    req.add_header('Content-Length', '%d' % length)
    response = urllib2.urlopen(req)
    res = response.read()
    response.close()