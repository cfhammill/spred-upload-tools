 #!/usr/bin/env python

"""
@author: Michael Joseph

Thanks to Wayne Lee (https://github.com/wy2lee/DCM_QA) and Ben Rowland 
(https://github.com/openmrslab/suspect), whose code greatly informed mine.

Description: Takes MR scan directories or entire MR session directories
             as input, copies them to a new target directory, anonymizes
             patient information in the headers, and re-labels the series
             descriptions according to SPReD conventions.

Code assumes certain input directory structure:

MR_session
|___001-localizer
|       0001.dcm
|       0002.dcm
|       ...
|___002-T1-SAG-MPRAGE-grappa2
|      0001.dcm
|      0002.dcm
|      ...
|___003-T2-AX-TSE-1-2mm-iso-grappa2
|      0001.dcm
|      0002.dcm
|      ...
|___MRS
|      14-MRS_GABA_Cere_fmap-1.rda
|      14-MRS_GABA_Cere_fmap-2.rda
|      ...
|___twix
       meas_MID39_MRS_GABA_Cere_fmap_1_FID45485.dat
       meas_MID40_MRS_GABA_Cere_fmap_2_FID45487.dat
       ...

Example usage:

---------------------------------

"""

"""
MR160
|___MR160-088-0001-01
   |___001-localizer
   |___002-T1_SAG_MPRAGE
   |___MRS
   |___twix

"""


import os
import re
import shutil
import dicom
import struct
import sys
import argparse
from getpass import getpass
import requests
import base64

from anonymize.dcm import anonymize_dcm
from anonymize.rda import anonymize_rda
from anonymize.twix import anonymize_twix

program_name = 'pond_anon.py'

# ---------- functions ----------

def load_site_codes(fname_site_codes):
    """
    Loads site code dictionary, splits text into keys and values
    """
    siteCodeDict = {}
    if not os.path.exists(fname_site_codes):
        raise SystemExit('ERROR - Parameter File - File not found: %s' % (fname_site_codes))

    file_site_codes = open(fname_site_codes, 'r')
    for line_site in file_site_codes:
        siteCodeDict[line_site.split(':')[0].strip(
            ' ')] = line_site.split(':')[1].strip(' \n')
    return siteCodeDict


def load_lut_scan_type(fname_lut_scan_type):
    """
    Loads lookup table for scan types
    """
    lut_scan_type = {}
    if not os.path.exists(fname_lut_scan_type):
        raise SystemExit('ERROR - Parameter File - File not found: %s' % (fname_subj_list))

    file_lut_scan_type = open(fname_lut_scan_type, 'r')
    for line_file in file_lut_scan_type:
        lut_scan_type[line_file.split(':')[0].strip(
            ' ')] = line_file.split(':')[1].strip(' \n')
    return lut_scan_type


def get_patientID(dir_input, siteCodeDict):
    dir_target = dir_input.split('/')[-1]
    subjectID_raw = dir_input.split('/')[-2]
    [Study, Site, Subj, Visit] = subjectID_raw.split('-')
    for code in siteCodeDict.keys():
        if siteCodeDict[code] == Site:
            SiteCode = code
    subjectID = 'PND03_%s_%s' % (SiteCode, Subj)
    sessionSuffix = '_%s_SE01_MR' % (Visit)
    sessionID = subjectID + sessionSuffix
    return subjectID, sessionID


def get_scan_type(scan_type):
    for key in lut_scan_type.keys():
        if re.search(key, scan_type, re.IGNORECASE):
            new_series_description = lut_scan_type[key]
            return new_series_description

# -------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog = "pond_anon.py",
        description = __doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-sc", "--scan_dirs", action="append", default=[],
        help="Anonymize the specified scan directories")
    group.add_argument(
        "-se", "--session_dirs", action="append", default=[],
        help="Anonymize the specified MR session directories")
    group.add_argument(
        "-sp", "--spred_left", action="store_true", default=[],
        help="Anonymize all MR sessions not currently on SPReD yet")
    parser.add_argument(
        "dir_out", action="store",
        help="Output directory for anonymized MR scans and sessions")
    parser.add_argument(
        "--lut_sites", dest="fname_site_codes", default="siteCodeDict.txt",
        help="Lut to convert internal site codes to SPReD site codes [default=siteCodeDict.txt]")
    parser.add_argument(
        "--lut_scans", dest="fname_lut_scan_type", default="lut_scan_type.txt",
        help="Lut to convert default series description into defined scan type [default=lut_scan_type.txt]")
    parser.add_argument(
        "--lut_dcm_list", dest="fname_dcm_list", default="anonymize/dcm_mod_basic.txt",
        help="Common dicom elements to wipe [default=dcm_mod_basic.txt]")
    parser.add_argument(
        "-c", "--clobber", action="store_true", dest="clobber", default=False,
        help="Allow the output file to be overwritten")
    parser.add_argument(
        "-v", "--verbose", action="store_true", dest="verbose", default=False, 
        help="Increase output verbosity")
    parser.add_argument(
        "-db", "--debug", action="store_true", dest="debug", default=False, 
        help="Run in debug mode")

    args = parser.parse_args()
    
    dir_out_base = args.dir_out
    # check that dir_out_base is an existing directory
    if not os.path.isdir(dir_out_base):
        raise SystemExit('ERROR - Output directory does not exist: %s' % (dir_out_base))

    # load site code dictionary and lookup tables (dicom headers to change, dicom scan types, mrs scan types)
    siteCodeDict = load_site_codes(args.fname_site_codes)
    lut_dcm_hdrs = load_dcm_list(args.fname_dcm_list)
    lut_scan_type = load_lut_scan_type(args.fname_lut_scan_type)

    # use argparse to identify whether incoming directory is a scan type or session and decide what to do
    if args.scan_dirs:
        scan_dirs = []
        for scan_dir in scan_dirs:
            if os.path.isdir(scan_dir):
                scan_dirs.append(scan_dir)
    
    elif args.session_dirs:
        for session_dir in session_dirs:
            if os.path.isdir(session_dir):
                scan_dirs = [os.path.abspath(os.path.join(session_dir, j)) for j in os.listdir(session_dir)]
    
    elif args.spred_left:
        spredToDo = diff_spred_local(local_src_dir)
        session_dirs = ['{0}/{1}'.format(local_src_dir, i) for i in spredToDo]
        for session_dir in session_dirs:
            scan_dirs = ['{0}/{1}'.format(session_dir, j) for j in os.listdir(session_dir)]

    for dir_input in scan_dirs:
        # anonymize scans differently depending on whether input directory is dicom, rda or twix
        if re.match('[0-9]{3}-*', dir_input.split('/')[-1]):
            [subjectID, sessionID] = get_patientID(dir_input, siteCodeDict)
            dir_input_clean = dir_input.replace('-','_')
            series_num = dir_input_clean.split('/')[-1].split('_')[0].lstrip("0")
            new_series_description = get_scan_type(dir_input_clean)
            dir_out_full = '%s/%s/%s/%s-%s/DICOM' % (dir_out_base, subjectID, sessionID, series_num, new_series_description)
            if new_series_description is None:
                print('ERROR - Unable to determine scan type for: %s') % (dir_input)
            else:
                shutil.copytree(dir_input, dir_out_full)
                list_dcm_files = os.listdir(dir_input)
                for fname_scan in list_dcm_files:
                    ds = dicom.read_file('%s/%s' % (dir_out_full, fname_scan))
                    ds.PatientName = subjectID
                    ds.PatientID = sessionID
                    ds.SeriesDescription = new_series_description
                    ds.SeriesNumber = series_num
                    ds.StudyDescription = "PND03"
                    ds.PatientBirthDate = "19900101"
                    ds.PatientAge = "0"
                    ds.PatientSize = "0"
                    ds.PatientWeight = "0"
                    ds.PatientSex = "0"
                    ds.PatientTelephoneNumbers = "0"
                    dicom.write_file('%s/%s' % (dir_out_full, fname_scan), ds)
        elif dir_input.split('/')[-1] == 'MRS':
            [subjectID, sessionID] = get_patientID(dir_input, siteCodeDict)
            scan_types = os.listdir(dir_input)
            for scan_type in scan_types:
                series_num = scan_type.split('_')[0]
                new_series_description = get_scan_type(scan_type_clean)
                dir_out_full = '%s/%s/%s/%s-%s/RDA' % (dir_out_base, subjectID, sessionID, series_num, new_series_description)
                if new_series_description is None:
                    print('ERROR - Unable to determine scan type for: %s/%s' % (dir_input, scan_type))
                else:
                    if not os.path.exists(dir_out_full):
                        os.makedirs(dir_out_full)
                    anonymize_rda(dir_input + '/' + scan_type, dir_out_full + '/' + scan_type) 
        elif dir_input.split('/')[-1] == 'twix':
            [subjectID, sessionID] = get_patientID(dir_input, siteCodeDict)
            scan_types = os.listdir(dir_input)
            for scan_type in scan_types:
                new_series_description = get_scan_type(scan_type)
                if new_series_description is None:
                    print('ERROR - Unable to determine scan type for: %s/%s' % (dir_input, scan_type))
                else:
                    dir_out_partial = '%s/%s/%s' % (dir_out_base, subjectID, sessionID)
                    dir_to_match = os.listdir(dir_out_partial)
                    for dir_match in dir_to_match:                
                        if re.search(('%s' % (new_series_description)), dir_match):
                            dir_out_full = '%s/%s/TWIX' % (dir_out_partial, dir_match)
                            if not os.path.exists(dir_out_full):
                                os.makedirs(dir_out_full)
                            anonymize_twix(dir_input + '/' + scan_type, dir_out_full + '/' + scan_type) 

if __name__ == '__main__':
    main()