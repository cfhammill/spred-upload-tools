import struct
import re

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
