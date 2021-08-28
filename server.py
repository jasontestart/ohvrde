from flask import Flask, render_template, request
from PyPDF4 import PdfFileReader
import extractor

app = Flask(__name__)

# Expecting PDF receipts to be smaller than 256K
app.config['MAX_CONTENT_LENGTH'] = 1024 * 256

@app.route('/ohvrde/')
def index():
    return render_template('index.html')

@app.route('/ohvrde/extract/', methods=['POST'])
def upload_file():
    uploaded_file = request.files['pdf_file']
    result = {}

    try:
        if extractor.is_pdf(uploaded_file.stream.read(2048)):
            pdf = PdfFileReader(uploaded_file.stream)
            page = pdf.getPage(0)
            page_content = page.extractText()
            result = extractor.parse_text(page_content)
            if extractor. get_signature(pdf):
                result['signed'] = 'True'
                result['message'] += ' The digital signature is present, but has not been validated.'
            else:
                result['signed'] = 'False'
            return result
        else:
            return "Try again with an actual PDF file.", 400
    except:
        return "Up to no good, are we?", 400

if __name__ == '__main__':
    app.run(debug = True)
