import re
import shutil

def load_dcm_list(fname_dcm_list):
    """
    Loads list of dicom headers to change and their new value
    """
    lut_dcm_hdrs = {}
    if not os.path.exists(fname_dcm_list):
        raise SystemExit('ERROR - Parameter File - File not found: %s' % (fname_dcm_list))

    file_dcm_list = open(fname_dcm_list, 'r')
    for line_dcm in file_dcm_list:
        lut_dcm_hdrs[line_dcm.split(':')[0].strip(
            ' ')] = line_dcm.split(':')[1].strip(' \n')
    return lut_dcm_hdrs


def check_scan_type(dir_curr_scan_clean, scan_type):
    """
    Function to check if current scan needs to be prepped
    Ignores processed DTI scans and Phoenix 
    """
    list_ignore = ['_ADC', '_TRACEW', '_FA', '_ColFA', 'PhoenixZIPReport']

    QA_THIS_SCAN = 1
    list_scan_type = scan_type.split(',')
    # make sure all keywords present in directory name
    for scan_keywords in list_scan_type:
        if dir_curr_scan_clean.find(scan_keywords) < 0:
            QA_THIS_SCAN = 0

    # make sure all ignore words are absent in directory name
    for ignore_keywords in list_ignore:
        if dir_curr_scan_clean.find(ignore_keywords) > -1:
            QA_THIS_SCAN = 0

    return QA_THIS_SCAN


def anonymize_dcm(dir_input):
    """
    Check if dir_target is one that requires modifications
    """

    [subjectID, sessionID] = get_ids(dir_input, siteCodeDict)
    dir_out_full = '%s/%s/%s/%s-%s' % (dir_out_base, subjectID, sessionID, dir_target_series_num, scanType)
    if os.path.exists(dir_out_full) and not args.clobber:
        raise SystemExit('ERROR - Output directory already exists. Turn on CLOBBER to overwrite: %s' % (dir_out_full))
    else:
        os.makedirs(dir_out_full)

    for scan_type in lut_scan_type:
        QA_THIS_SCAN = check_scan_type(dir_target_clean, scan_type)
        # print QA_THIS_SCAN
        if QA_THIS_SCAN:
            new_scanType = get_scan_type(scan_type)
            new_subjectID = subjectID
            new_sessionName = '%s_%s' % (subjectID, sessionSuffix)
        # print dir_target, new_subjectID, new_sessionName, new_scanType

            # need to include series name to differentiate repeats of same ScanType
            # Check for output directories, create if needed
            if not os.path.exists(dir_out_base):
                run_cmd('mkdir ' + dir_out_base, args.debug, args.verbose)
            if not os.path.exists(dir_out_base + '/' + subjectID):
                run_cmd('mkdir ' + dir_out_base + '/' + subjectID, args.debug, args.verbose)
            if not os.path.exists(dir_out_base + '/' + subjectID + '/' + new_sessionName):
                run_cmd('mkdir ' + dir_out_base + '/' + subjectID + '/' + new_sessionName, args.debug, args.verbose)

            dir_out_full = '%s/%s/%s/%s-%s' % (dir_out_base,
                                               subjectID,
                                               new_sessionName,
                                               dir_target_series_num,
                                               new_scanType)

        # Check for specific output directory, exit if not clobber
            if os.path.exists(dir_out_full) and not args.clobber:
                raise SystemExit('ERROR - Output directory already exists, turn on CLOBBER to overwrite: %s' % (dir_out_full))
            else:
                shutil.copytree(dir_input, dir_out_full)

            # make newly created directory writeable
            # chmod +w -R dir_out_full
            if os.access(dir_out_full, os.W_OK) == False:
                os.chmod(dir_out_full, stat.S_IWUSR)

            list_dcm_files = os.listdir(dir_input)

            for fname_scan in list_dcm_files:

                dcmodify_string = '-i "(0010,0010)=%s" -i "(0010,0020)=%s" -i "(0008,103e)=%s" -i "(0020,0011)=%s"' % (
                    new_subjectID, new_sessionName, new_scanType, dir_target_series_num.lstrip('0'))
                for curr_dcm_hdr_index in lut_dcm_hdrs:
                    curr_dcm_hdr_value = lut_dcm_hdrs[curr_dcm_hdr_index].strip(
                        '\n')
                    dcmodify_string = '%s -i "(%s)=%s"' % (
                        dcmodify_string, curr_dcm_hdr_index, curr_dcm_hdr_value)
                cmd_dcmodify = 'dcmodify %s %s/%s' % (
                    dcmodify_string, dir_out_full, fname_scan)
                run_cmd(cmd_dcmodify, args.debug, args.verbose)

                cmd_rmbak = 'rm -f %s/%s.bak' % (dir_out_full, fname_scan)
                run_cmd(cmd_rmbak, args.debug, args.verbose)
