import magic

# take the contents and see what we can extract
def parse_text(contents):
    result = {}

    #First, check for some key terms
    keyterms = ['Ministry of Health', 'Ministère de la Santé', 'Numéro de la carte Santé', 'Organisme agréé']
    for term in keyterms:
        if contents.find(term) == -1:
            result['message'] = "Does not appear to be a receipt from Ontario Health."
            return result

    result["message"] = "Appears to be a receipt from Ontario Health."

    name_seen = False
    hc_seen = False
    org_seen = False
    for line in contents.splitlines():
        if name_seen:
            result['name'] = line.strip()
            name_seen = False
        elif hc_seen:
            if line.strip().startswith("#") or line.find('Date de naissance') > 0:
                continue
            else:
                result['dob'] = line.strip()
                hc_seen = False
        elif org_seen:
            if 'org' in result.keys():
                sub = line[:4]
                if sub in ['Note', '----', 'Plea', 'This', 'Your']:
                    org_seen = False
                else:
                    result['org'] += f" {line.strip()}"
            else:
                result['org'] = line.strip()

        elif line.find('Name') == 0:
            name_seen = True
        elif line.find('Numéro de la carte Santé') > 0:
            hc_seen = True
        elif line.find('You have received') != -1:
            english = line.split('/')[0]
            result['num_doses'] = str([int(s) for s in english.split() if s.isdigit()][0])
        elif line.find('Organisme agréé') > 0:
            org_seen = True

    return result

def is_pdf(data):
    file_type = magic.from_buffer(data, mime=True)
    if file_type == 'application/pdf':
        return True
    else:
        return False

def get_signature(pdf):
    try:
        sig = bytearray(pdf.getFields()['Signature1']['/V']['/Contents'])
    except:
        return False
    return True

if __name__ == '__main__':
    from PyPDF4 import PdfFileReader
    import sys

    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <filename>")
        quit()
    
    path = sys.argv[1]

    with open(path, 'rb') as f:
        if not is_pdf(f.read(2048)):
            print('Not a PDF.')
            quit()

        pdf = PdfFileReader(f)
        
        page = pdf.getPage(0)
        page_content = page.extractText()
        result = parse_text(page_content)
        if get_signature(pdf):
            result['signed'] = 'True'
            result['message'] += ' The digital signature is present, but has not been validated.'
        else:
            result['signed'] = 'False'
        print(result)
