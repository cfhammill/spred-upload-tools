#!/usr/bin/python

from optparse import OptionParser, Option, OptionValueError
import datetime
import string
import glob
import os, shlex, subprocess
import numpy
import fnmatch
from diff_spred_local_alt import spredToDo

program_name = 'dcm_clean.py'

#*************************************************************************************
# FUNCTIONS

# General utility function to call system commands
def run_cmd(sys_cmd, debug, verbose):
# one line call to output system command and control debug state
    if verbose:
        print sys_cmd
    if not debug:
        p = subprocess.Popen(sys_cmd, stdout = subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, errors = p.communicate()
        if verbose:
            print output, errors
        return output, errors
    else:
        return '',''

def load_dcm_list(fname_dcm_list):
    lut_dcm_hdrs={}
#   Loads list of dicom headers to change, and their new value
    if not os.path.exists(fname_dcm_list):
        raise SystemExit, 'ERROR - Parameter File - File not found: %s' % (fname_dcm_list,) 
        
    file_dcm_list = open(fname_dcm_list,'r')
    for line_dcm in file_dcm_list:
        lut_dcm_hdrs[line_dcm.split(':')[0].strip(' ')] = line_dcm.split(':')[1].strip(' \n')
    return lut_dcm_hdrs

def load_lut_scan_type(fname_lut_scan_type):
#   Loads lut for scan_types
    lut_scan_type={}
    if not os.path.exists(fname_lut_scan_type):
        raise SystemExit, 'ERROR - Parameter File - File not found: %s' % (fname_subj_list,) 
        
    file_lut_scan_type = open(fname_lut_scan_type,'r') 
    for line_file in file_lut_scan_type:
        lut_scan_type[line_file.split(':')[0].strip(' ')] = line_file.split(':')[1].strip(' \n')
    return lut_scan_type

def check_scan_type(dir_curr_scan_clean, scan_type):
# Function to check if current scan needs to be prepped
    list_ignore = ['_ADC','_TRACEW','_FA','_ColFA']   # processed DTI scans to ignore

    QA_THIS_SCAN = 1
    list_scan_type = scan_type.split(',')
    # make sure all keywords present in directory name
    for scan_keywords in list_scan_type:
        if dir_curr_scan_clean.find(scan_keywords)<0:
            QA_THIS_SCAN = 0
            
    # make sure all ignore words are absent in directory name
    for ignore_keywords in list_ignore:
        if dir_curr_scan_clean.find(ignore_keywords)>-1:
            QA_THIS_SCAN = 0
            
    return QA_THIS_SCAN
      
#**********************************************************************
    
def main():
    usage = "Usage: "+program_name+" <options> dir_out_base \n" + \
            "   or  "+program_name+" --help";
    parser = OptionParser(usage)
    parser.add_option("--lut_ST", type="string", dest="fname_lut_scan_type",
                        default="lut_scan_type.cfg", help="Lut to convert default Scan Description into defined ScanType [default = lut_scan_type.cfg]")
    parser.add_option("--lut_dcm_list", type="string", dest="fname_dcm_list",
                        default="dcm_mod_basic.txt", help="Common dicom elements to wipe [default = %s]")
    parser.add_option("-c","--clobber", action="store_true", dest="clobber",
                        default=0, help="overwrite output file")
    parser.add_option("-v","--verbose", action="store_true", dest="verbose",
                        default=0, help="Verbose output")
    parser.add_option("-d","--debug", action="store_true", dest="debug",
                        default=0, help="Run in debug mode")

    options, args = parser.parse_args()

    if len(args) == 1:
        dir_out_base = args
    else:
        parser.error("Incorrect number of arguments")
    
    lut_dcm_hdrs = load_dcm_list(options.fname_dcm_list)
    lut_scan_type = load_lut_scan_type(options.fname_lut_scan_type)    
        
    session_dirs = ['/micehome/mjoseph/data8/mrdata/MR160/{0}'.format(i) for i in spredToDo]
    for session_dir in session_dirs:
        scan_dirs = os.listdir(session_dir)
        scan_dir = ['{0}/{1}'.format(session_dir, j) for j in scan_dirs]
        for dir_input in scan_dir:
            dir_target = dir_input.split('/')[-1]
            dir_target_clean = dir_target.replace('-','_')   # remove variability of - or _

            dir_target_series_num = dir_target_clean.split('_')[0]

            # pull subjectID from directory structure
            subjectID_raw = dir_input.split('/')[-2]
            [Study, Site, Subj, Visit] = subjectID_raw.split('-')

            if Site=='088':
                SiteCode = 'HSC'
            else: # Site=='105':
                SiteCode = 'HBK'

            subjectID = 'PND03_%s_%s' % (SiteCode,Subj)
            sessionSuffix = '%s_SE01_MR' % (Visit,)
    
#    print lut_scan_type
    # Check if dir_target is one that requires modifications    
            for scan_type in lut_scan_type:
                QA_THIS_SCAN = check_scan_type(dir_target_clean, scan_type) 
#               print QA_THIS_SCAN
                if QA_THIS_SCAN:
                    new_scanType = lut_scan_type[scan_type]
                    new_subjectID = subjectID
                    new_sessionName = '%s_%s' % (subjectID,sessionSuffix)
#            print dir_target, new_subjectID, new_sessionName, new_scanType
            
            # need to include series name to differentiate repeats of same ScanType
            # Check for output directories, create if needed
                    if not os.path.exists(dir_out_base):
                        run_cmd('mkdir ' + dir_out_base, options.debug, options.verbose)
                    if not os.path.exists(dir_out_base + '/' + subjectID):
                        run_cmd('mkdir ' + dir_out_base + '/' + subjectID, options.debug, options.verbose)
                    if not os.path.exists(dir_out_base + '/' + subjectID + '/' + new_sessionName):
                        run_cmd('mkdir ' + dir_out_base + '/' + subjectID + '/' + new_sessionName, options.debug, options.verbose)
            
                    dir_out_full = '%s/%s/%s/%s-%s' % (dir_out_base,subjectID,new_sessionName, dir_target_series_num, new_scanType)
        
            # Check for specific output directory, exit if not clobber
                    if  os.path.exists( '%s' % (dir_out_full, )) and not options.clobber:
                        raise SystemExit, '* ERROR - Output directory already exists, turn on CLOBBER to overwrite: %s' % ((dir_out_full,)) 
                    else:
                        cmd_duplicate = ('cp -r %s %s/') % (dir_input, dir_out_full)
                  
                    run_cmd(cmd_duplicate, options.debug, options.verbose)
            
                    # make newly created directory writeable
                    # chmod +w -R dir_out_full
                    cmd_modperm = ('chmod +w -R %s') % (dir_out_full)            
                    run_cmd(cmd_modperm, options.debug, options.verbose)

                    list_dcm_files = os.listdir(dir_input)

                    for fname_scan in list_dcm_files:
                    # print fname_scan
                        dcmodify_string = '-i "(0010,0010)=%s" -i "(0010,0020)=%s" -i "(0008,103e)=%s" -i "(0020,0011)=%s"' % (new_subjectID, new_sessionName, new_scanType, dir_target_series_num)
                        for curr_dcm_hdr_index in lut_dcm_hdrs:
                            curr_dcm_hdr_value = lut_dcm_hdrs[curr_dcm_hdr_index].strip('\n')
                            dcmodify_string = '%s -i "(%s)=%s"' % (dcmodify_string, curr_dcm_hdr_index, curr_dcm_hdr_value)
                        cmd_dcmodify = 'dcmodify %s %s/%s' % (dcmodify_string, dir_out_full, fname_scan)
                        run_cmd(cmd_dcmodify, options.debug, options.verbose)
                
                        # remove backup files that were created when changing headers
                        cmd_rmbak = 'rm -f %s/%s.bak' % (dir_out_full, fname_scan)
                        run_cmd(cmd_rmbak, options.debug, options.verbose)
            
if __name__ == '__main__' :
    main()
