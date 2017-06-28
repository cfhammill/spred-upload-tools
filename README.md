---
output: html_document
---
# spred-upload-tools

### Current Version

2.00

### Authors
Michael Joseph
Thanks to Wayne Lee (https://github.com/wy2lee/DCM_QA) and Ben Rowland (https://github.com/openmrslab/suspect), whose code greatly informed mine.

## Introduction

This is some brief documentation for the work I did for the Provice of Ontario Neurodevelopmental Network ([POND][2]) and the Ontario Brain Institute (OBI). The OBI is working on a neuroinformatics platform called [Brain-CODE][3]. It was my job to upload the existing human brain imaging data into the imaging side of Brain-CODE. The imaging side of Brain-CODE uses the Stroke Patient Recovery Research Database ([SPReD][4]), which is based off of the [XNAT][5] platform (version 1.6.3).

The upload process uses a Python script ([diff_spred_local.py][6]) to determine which MR sessions in the local data directories haven't been uploaded to SPReD yet. Another Python script ([dcm_clean.py][7]) takes those MR sessions, de-identifies the patient data and re-labels the scan directories to be compatible with the SPReD naming conventions. 

To learn how to use these scripts, consult the Workflow below and make sure you have everything installed listed in the Dependencies section.

## Workflow
1. diff_spred_local.py: identifies which MR sessions need to be uploaded to SPReD
    - retrieves lists of MR sessions in local directory and on SPReD and determines the difference between the two
        - specify local data directory path
        - ensure that siteCodeDict.txt (site code dictionary) is up to date with the sites your data were obtained from
        - enter SPReD username and password in command line
2. dcm_clean.py: organizes and anonymizes MR session directories
    - copies MR session directories, re-labels them according to SPReD naming conventions and de-identifies DICOM headers
    - dcm_mod_basic.txt contains DICOM headers that are changed to set values globally
    ```
    0008,1030 : PND03           (Study Description)
    0010,0030 : 19900101        (Patient Birthdate)
    0010,0040 : 0               (Patient Sex)
    0010,1010 : 0               (Patient Age)
    0010,1020 : 0               (Patient Size)
    0010,1030 : 0               (Patient Weight)
    0010,2154 : 0               (Patient Telephone Numbers)
    ```
    - DICOM headers that are changed for each scan type in an MR session include:
    ```
    0008,103e: "Scan Type"      (Series Description)
    0010,0010: "Subject ID"     (Patient Name)
    0010,0020: "MR Session ID"  (Patient ID)
    0020,0011: "Scan Series #"  (Series Number) --> added because some scans had duplicated series numbers
    ```
    - ensure that lut_scan_type.cfg (scan type dictionary) is up to date with all of the scanning modalities involved
3. uploader.py: upload to SPReD

## Dependencies
1. Python 3.5 (os.scandir() function is a new feature)
2. Python packages to install:
    - requests
    - lxml
    - urllib2
    - numpy
    - [pyxnat][8]
3. dcmodify (part of the [DICOM Toolkit] [9]) `sudo apt-get install dcmtk`

## To Do
- add step to zip MR session directories
- allow dcm_clean.py to take different types of input directories (eg. specific scanning directories, multiple MR sessions, etc.)

<!---
References
-->
[1]: https://github.com/wy2lee/DCM_QA 
[2]: http://pond-network.ca/home/
[3]: https://braincode.ca/
[4]: https://spred.braincode.ca/
[5]: http://www.xnat.org/
[6]: https://github.com/josephmje/SPReD_Upload_Tools/blob/master/diff_spred_local.py
[7]: https://github.com/josephmje/SPReD_Upload_Tools/blob/master/dcm_clean.py
[8]: https://github.com/pyxnat/pyxnat
[9]: http://support.dcmtk.org/docs/index.html
