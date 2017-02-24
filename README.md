---
output: html_document
---
# SPReD DICOM Upload Tools

### Current Version

1.00

### Authors
Originally conceived by [Wayne Lee] [1] with modifications by Michael Joseph

## Introduction

This is some brief documentation for the work I did for the Provice of Ontario Neurodevelopmental Network [POND][2] and the Ontario Brain Institute (OBI). The OBI is working on a neuroinformatics platform called [Brain-CODE][3]. It was my job to upload the existing human brain imaging data into the imaging side of Brain-CODE. The imaging side of Brain-CODE uses the Stroke Patient Recovery Research Database ([SPReD][4]), which is based off of the [XNAT][5] platform (version 1.6.3).

The upload process uses a Python script (diff_spred_local.py) to determine which MR sessions in the local data directories haven't been uploaded to SPReD yet. Another Python script (dcm_clean.py) takes those MR sessions, de-identifies the patient data and re-labels the scan directories to be compatible with the SPReD naming conventions. 

To learn how to use these scripts, consult the Workflow below and make sure you have everything installed listed in the Dependencies section.

## Workflow

## Dependencies
1. Python 2.7+
2. Python packages to install:
    - requests
    - lxml
    - urllib2
    - numpy
    - pyxnat
3. dcmodify (part of the [DICOM Toolkit] [6])

<!---
References
-->
[1]: https://github.com/wy2lee/DCM_QA 
[2]: http://pond-network.ca/home/
[3]: https://braincode.ca/
[4]: https://spred.braincode.ca/
[5]: http://www.xnat.org/
[6]: http://support.dcmtk.org/docs/index.html
