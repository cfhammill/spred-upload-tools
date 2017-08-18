#!/usr/bin/env python3

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

# import modules
import os
import re
import shutil
import dicom as pydicom # pydicom v1.0+ is imported as pydicom
import struct
import sys
from getpass import getpass
import requests
import argparse

# ---------- functions ----------

def load_lut(fname_lut):
    """
    Loads lookup table, splits text into keys and values
    """
    lut = {}
    if not os.path.exists(fname_lut):
        raise SystemExit('ERROR - Parameter File - File not found: %s' % (fname_lut))

    file_obj = open(fname_lut, 'r')
    for line in file_obj:
        lut[line.split(':')[0].strip(' ')] = line.split(':')[1].strip(' \n')
    return lut


def get_patientID(dir_input, siteCodeDict):
    """
    Uses directory structure to get patientID, converts to SPReD conventions
    and outputs a subjectID and sessionID
    """
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


def get_scan_type(scan_type, lut_scan_type):
    """
    Matches filename to lookup table keys and outputs a standardized scan type
    """
    for key in lut_scan_type.keys():
        if re.search(key, scan_type, re.IGNORECASE):
            new_series_description = lut_scan_type[key]
            return new_series_description


def diff_spred_local(local_src_dir, siteCodeDict):
    MR160local = []
    for session in os.scandir(local_src_dir):
        if session.is_dir():
            MR160local.append(session.name)

    MR160local = filter(lambda x: re.match('MR160-\d+-\d+-\d+$', x) is not None, MR160local)

    # identify MR sessions already uploaded to SPReD
    user = input("Username: ")
    passwd = getpass("Password for " + user + ": ")
    usrPass = (user, passwd)

    print("Input the desired projects. If entering multiple projects, use commas between them without spaces.")
    projects = input("Projects on SPReD: ")

    url = "https://spred.braincode.ca/spred/data/archive/experiments?format=json&columns=xnat:mrSessionData/label&project=%s" % (projects)

    response = requests.get(url, auth=usrPass)
    result = response.json()
    result_body = result['ResultSet']['Result']
    MR160spred = []
    for item in result_body:
        label = item['xnat:mrsessiondata/label']
        MR160spred.append(label)

    # convert labeling style of MR160spred to MR160local
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


def anonymize_rda_hdr(header_string, anonymized_filename):
    """
    Removes the PHI from the supplied rda header and returns the sanitized version.
    This consists of:
    1) Replacing the patient name and id with strings
    2) Replacing the patient birthday with 19900101
    3) Replacing the patient gender with the letter O
    4) Replacing the patient weight and age with the number 0
    5) Replacing the study description with the string PND03
    6) Replacing the protocol name and series description with SPReD labeling conventions
    
    Parameters
    ----------
    header_string : str
        The header string to be anonymized

    Returns
    -------
    str
        The anonymized version of the header.
    """

    patient_name = "(PatientName: )(.+)(\r\n)"
    patient_id = "(PatientID: )(.+)(\r\n)"
    patient_birthday = "(PatientBirthDate: )(.+)(\r\n)"
    patient_gender = "(PatientSex: )(.+)(\r\n)"
    patient_age = "(PatientAge: )([0-9]{3}Y)(\r\n)"
    patient_weight = "(PatientWeight: )(\d+.\d*)(\r\n)"
    study_description = "(StudyDescription: )(.+)(\r\n)"
    #protocol_name = "(ProtocolName: )(.+)(\r\n)"
    series_description = "(SeriesDescription: )(.+)(\r\n)"

    [subjectID, sessionID, new_series_description] = [
        anonymized_filename.split('/')[-5], 
        anonymized_filename.split('/')[-4],
        (anonymized_filename.split('/')[-3]).split('-')[-1]]

    header_string = re.sub(patient_name, lambda match: "".join(
        (match.group(1), subjectID, match.group(3))), 
        header_string)

    header_string = re.sub(patient_id, lambda match: "".join(
        (match.group(1), sessionID, match.group(3))), 
        header_string)

    header_string = re.sub(patient_birthday, lambda match: "".join(
        (match.group(1), "19900101", match.group(3))), 
        header_string)

    header_string = re.sub(patient_gender, lambda match: "".join(
        (match.group(1), "O", match.group(3))), 
        header_string)        

    header_string = re.sub(patient_age, lambda match: "".join(
        (match.group(1), "0", match.group(3))), 
        header_string)

    header_string = re.sub(patient_weight, lambda match: "".join(
        (match.group(1), "0", match.group(3))), 
        header_string)

    header_string = re.sub(study_description, lambda match: "".join(
        (match.group(1), "PND03", match.group(3))), 
        header_string)

    #header_string=re.sub(protocol_name, lambda match: "".join(
    #    (match.group(1), new_series_description, match.group(3))), 
    #    header_string)

    header_string=re.sub(series_description, lambda match: "".join(
        (match.group(1), new_series_description, match.group(3))), 
        header_string)

    return header_string


def anonymize_rda(filename, anonymized_filename):
    with open(filename, 'rb') as fin:

        # read binary file until it detects a null character
        aByte = fin.read(1)
        while aByte and ord(aByte) != 0:
            aByte = fin.read(1)
    
        # find position of the null character and subtract 1
        pos = fin.tell() - 1
        
        # reset file to read from beginning
        fin.seek(0)

        # read header until byte before null
        header_string = fin.read(pos).decode('ascii')  

        anonymized_header = anonymize_rda_hdr(header_string, anonymized_filename)

        with open(anonymized_filename, 'wb') as fout:
            
            fout.write(anonymized_header.encode('ascii'))
            fout.write(fin.read())


def anonymize_twix_hdr(header_string):
    """Removes the PHI from the supplied twix header and returns the sanitized version.
    This consists of:
    1) Replacing the patient id and name with strings of lower case x
    characters.
    2) Replacing the patient birthday with 19900101
    3) Replacing the patient gender with the number 0
    4) Replacing all digits in the patient age, weight and height with 0s
  
    Parameters
    ----------
    header_string : str
        The header string to be anonymized

    Returns
    -------
    str
        The anonymized version of the header.
    """

    patient_name = "(<ParamString.\"t?Patients?Name\">\s*\{\s*\")(.+)(\"\s*\}\n)"
    patient_id = "(<ParamString.\"PatientID\">\s*\{\s*\")(.+)(\"\s*\}\n)"
    patient_birthday = "(<ParamString.\"PatientBirthDay\">\s*\{\s*\")(.+)(\"\s*\}\n)"
    patient_gender = "(<ParamLong.\"l?PatientSex\">\s*\{\s*)(\d+)(\s*\}\n)"
    patient_age = "(<ParamDouble.\"flPatientAge\">\s*\{\s*<Precision> \d+\s*)(\d+\.\d*)(\s*\}\n)"
    patient_weight = "(<ParamDouble.\"flUsedPatientWeight\">\s*\{\s*<Precision> \d+\s*)(\d+\.\d*)(\s*\}\n)"
    patient_height = "(<ParamDouble.\"flPatientHeight\">\s*\{\s*<Unit> \"\[mm\]\"\s*<Precision> \d+\s*)(\d+\.\d*)(\s*\}\n)"

    header_string = re.sub(patient_name, lambda match: "".join(
        (match.group(1), ("x" * (len(match.group(2)))), match.group(3))),
        header_string)

    header_string = re.sub(patient_id, lambda match: "".join(
        (match.group(1), ("x" * (len(match.group(2)))), match.group(3))),
        header_string)

    header_string = re.sub(patient_birthday, lambda match: "".join(
        (match.group(1), "19900101", match.group(3))),
        header_string)

    header_string = re.sub(patient_gender, lambda match: "".join(
        (match.group(1), "0", match.group(3))),
        header_string)

    header_string = re.sub(patient_age, lambda match: "".join(
        (match.group(1), re.sub(r"\d", "0", match.group(2)), match.group(3))),
        header_string)

    header_string = re.sub(patient_weight, lambda match: "".join(
        (match.group(1), re.sub(r"\d", "0", match.group(2)), match.group(3))),
        header_string)

    header_string = re.sub(patient_height, lambda match: "".join(
        (match.group(1), re.sub(r"\d", "0", match.group(2)), match.group(3))),
        header_string)

    return header_string


def anonymize_twix(filename, anonymized_filename):
    with open(filename, 'rb') as fin:
        
        with open(anonymized_filename, 'wb') as fout:
            
            # first four bytes are the size of the header
            header_size = struct.unpack("I", fin.read(4))[0]

            # read the rest of the header minus the four bytes we already read
            header = fin.read(header_size - 4)
            # for some reason the last 24 bytes of the header contain some stuff that
            # is not a string, I don't know what it is
            header_string = header[:-24].decode('latin-1')

            anonymized_header = anonymize_twix_hdr(header_string)

            fout.write(struct.pack("I", header_size))
            fout.write(anonymized_header.encode('latin-1'))
            fout.write(header[-24:])
            fout.write(fin.read())

def anonymize(dir_input, dir_out_base, siteCodeDict, lut_dcm_type, lut_dcm_hdr, lut_rda_type, lut_twix_type):
    # anonymize dicom
    if re.match('[0-9]{3}-*', dir_input.split('/')[-1]):
        [subjectID, sessionID] = get_patientID(dir_input, siteCodeDict)
        dir_input_clean = dir_input.replace('-','_')
        series_num = int(dir_input_clean.split('/')[-1].split('_')[0].lstrip("0"))
        new_series_description = get_scan_type(dir_input_clean, lut_dcm_type)

        # series number is stripped of leading zeroes
        # pad with zeroes here so directories are listed in proper order
        dir_out_full = '%s/%s/%s/%03d-%s/DICOM' % (dir_out_base, subjectID, sessionID, series_num, new_series_description)
        if new_series_description is None:
            print('ERROR - Unable to determine scan type for: %s' % dir_input)
        else:
            shutil.copytree(dir_input, dir_out_full)
            os.system('chmod +w -R %s' % (dir_out_full))
            list_dcm_files = os.listdir(dir_input)
            for fname_scan in list_dcm_files:
                ds = pydicom.read_file('%s/%s' % (dir_out_full, fname_scan))
                ds.PatientName = subjectID
                ds.PatientID = sessionID
                ds.SeriesDescription = new_series_description
                ds.SeriesNumber = series_num
                # instead of this, do for loop (eg. for each key in lut_dcm_hdr, do ...)
                for key in lut_dcm_hdr:
                    setattr(ds, key, lut_dcm_hdr[key])
                pydicom.write_file('%s/%s' % (dir_out_full, fname_scan), ds)

    # anonymize rda
    if dir_input.split('/')[-1] == 'MRS':
        [subjectID, sessionID] = get_patientID(dir_input, siteCodeDict)
        scan_types = os.listdir(dir_input)
        for scan_type in scan_types:
            if scan_type.endswith('.rda'):
                (series_num, scan_name) = scan_type.split('-', 1)
                series_num = int(series_num)
                new_series_description = get_scan_type(scan_name, lut_mrs_type)
                dir_out_full = '%s/%s/%s/%03d-%s/RDA' % (dir_out_base, subjectID, sessionID, series_num, new_series_description)
                if new_series_description is None:
                    print('ERROR - Unable to determine scan type for: %s/%s' % (dir_input, scan_type))
                else:
                    if not os.path.exists(dir_out_full):
                        os.makedirs(dir_out_full)
                    # output rda file doesn't include series_num, as per Steve Arnott's request
                    anonymize_rda(dir_input + '/' + scan_type, dir_out_full + '/' + scan_name) 
    # anonymize twix
    if dir_input.split('/')[-1] == 'twix':
        [subjectID, sessionID] = get_patientID(dir_input, siteCodeDict)
        scan_types = os.listdir(dir_input)
        for scan_type in scan_types:
            if scan_type.endswith('.dat'):
                new_series_description = get_scan_type(scan_type, lut_twix_type)
                if new_series_description is None:
                    print('ERROR - Unable to determine scan type for: %s/%s' % (dir_input, scan_type))
                else:
                    dir_out_partial = '%s/%s/%s' % (dir_out_base, subjectID, sessionID)
                    dir_to_match = os.listdir(dir_out_partial)
                    dir_match = [x for x in dir_to_match if '%s' % (new_series_description) in x]
                    if not len(dir_match) == 1:
                        print('ERROR - Unable to determine matching directory for: %s/%s' % (dir_input, scan_type))
                    else:     
                        dir_out_full = '%s/%s/TWIX' % (dir_out_partial, dir_match[0])
                        if not os.path.exists(dir_out_full):
                            os.makedirs(dir_out_full)
                        anonymize_twix(dir_input + '/' + scan_type, dir_out_full + '/' + scan_type) 

# -------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog = "pond_anon.py",
        description = __doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-s", "--scan_dirs", action="append", default=[],
        help="Anonymize the specified scan directories")
    group.add_argument(
        "-e", "--session_dirs", action="append", default=[],
        help="Anonymize the specified MR session directories")
    group.add_argument(
        "-p", "--spred_left", default=("/micehome/mjoseph/data8/mrdata/MR160"),
        help="Anonymize all MR sessions not currently on SPReD yet")
    parser.add_argument(
        "-d", "--dir_out",
        help="Output directory for anonymized MR scans and sessions")
    parser.add_argument(
        "--lut_sites", dest="fname_site_codes", default="siteCodeDict.txt",
        help="Lut to convert internal site codes to SPReD site codes [default=siteCodeDict.txt]")
    parser.add_argument(
        "--lut_dcm_type", dest="fname_dcm_type", default="lut_dcm_type.txt",
        help="Lut to convert default dicom series description into defined scan type [default=lut_dcm_type.txt]")
    parser.add_argument(
        "--lut_dcm_hdr", dest="fname_dcm_hdr", default="dcm_mod_basic.txt",
        help="Common dicom elements to wipe [default=dcm_mod_basic.txt]")
    parser.add_argument(
        "--lut_rda_type", dest="fname_rda_type", default="lut_rda_type.txt",
        help="Lut to convert default rda series description into defined scan type [default=lut_rda_type.txt]")
    parser.add_argument(
        "--lut_twix_type", dest="fname_twix_type", default="lut_twix_type.txt",
        help="Lut to convert default twix series description into defined scan type [default=lut_twix_type.txt]")    
    parser.add_argument(
        "-c", "--clobber", action="store_true", dest="clobber", default=False,
        help="Allow the output file to be overwritten")

    args = parser.parse_args()

    dir_out_base = args.dir_out
    # check that dir_out_base is an existing directory
    if not os.path.isdir(dir_out_base):
        raise SystemExit('ERROR - Output directory does not exist: %s' % (dir_out_base))

    # load site code dictionary and lookup tables (dicom headers to change, dicom scan types, mrs scan types)
    siteCodeDict = load_lut(args.fname_site_codes)
    lut_dcm_type = load_lut(args.fname_dcm_type)
    lut_dcm_hdr = load_lut(args.fname_dcm_hdr)
    lut_rda_type = load_lut(args.fname_rda_type)
    lut_twix_type = load_lut(args.fname_twix_type)

    # use argparse to identify input directory
    if args.scan_dirs:
        scan_dirs = args.scan_dirs
        for scan_dir in scan_dirs:
            if os.path.isdir(scan_dir):
                anonymize(scan_dir, dir_out_base, siteCodeDict, lut_dcm_type, lut_dcm_hdr, lut_rda_type, lut_twix_type)
    elif args.session_dirs:
        session_dirs = args.session_dirs
        for session_dir in session_dirs:
            if os.path.isdir(session_dir):
                scan_dirs = [os.path.abspath(os.path.join(session_dir, j)) for j in os.listdir(session_dir)]    
                for dir_input in scan_dirs:
                    anonymize(dir_input, dir_out_base, siteCodeDict, lut_dcm_type, lut_dcm_hdr, lut_rda_type, lut_twix_type)    
    elif args.spred_left:
        spred_left = args.spred_left 
        spredToDo = diff_spred_local(spred_left, siteCodeDict)
        session_dirs = ['{0}/{1}'.format(spred_left, i) for i in spredToDo]
        for session_dir in session_dirs:
            scan_dirs = ['{0}/{1}'.format(session_dir, j) for j in os.listdir(session_dir)]
            for dir_input in scan_dirs:
                anonymize(dir_input, dir_out_base, siteCodeDict, lut_dcm_type, lut_dcm_hdr, lut_rda_type, lut_twix_type)


if __name__ == '__main__':
    main()
