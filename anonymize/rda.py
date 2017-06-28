import re

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
    protocol_name = "(ProtocolName: )(.+)(\r\n)"
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

    header_string=re.sub(protocol_name, lambda match: "".join(
        (match.group(1), new_series_description, match.group(3))), 
        header_string)

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

