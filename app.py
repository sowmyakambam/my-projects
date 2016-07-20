
import smtplib
import mimetypes

import email
import email.mime.application
from email.MIMEBase import MIMEBase
import os
from email import *
from email.mime import *

import tarfile
import tempfile
import zipfile

from email import encoders
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename

# Initialize the Flask application
app = Flask(__name__)
msg = email.mime.Multipart.MIMEMultipart()

msg['Subject'] = 'Greetings'


body = email.mime.Text.MIMEText("""Hello, how are you? I am fine.
You have got attachment(s).""")
msg.attach(body)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'E://uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','zip','tar'])

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    # print '.' in filename and \
           # filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def index1():
    return render_template('about.html')

# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():

    sendmail= request.form['sendermail']
    print sendmail
    recipientmail=request.form['recipientmail']
    msg['From'] = sendmail
    msg['To'] = recipientmail
    # Get the name of the uploaded files
    uploaded_files = request.files.getlist('file[]')
    filenames = []
    zf = tempfile.TemporaryFile(prefix='mail', suffix='.zip')
    for file in uploaded_files:
        # Check if the file is one of the allowed types/extensions
        if file and allowed_file(file.filename):
            ctype = 'application/octet-stream'
            subtype = ctype.split('/', 1)
            # Make the filename safe, remove unsupported chars
            filename = secure_filename(file.filename)
            # Move the file form the temporal folder to the upload
            # folder we setup
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            f=os.path.join(app.config['UPLOAD_FOLDER'], filename)

            print "filename"+f
            # Save the filename into a list
            filenames.append(filename)

            print "After appending files"

            # with tarfile.open("eeg_files.tar", "a") as tarf:
            #     filename3="eeg_files.tar"
            #     ep_dir = tarfile.TarInfo("uploadedfiles")
            
            #     ep_dir.type = tarfile.DIRTYPE
            #     ep_dir.mode = 0o777
            #     tarf.addfile(ep_dir)

            #     tarf.add(f)

            
            zip = zipfile.ZipFile(zf, 'a')
            zip.write(f)
            print "zip file is" +f
            zip.close()
            zf.seek(0)


    att = MIMEBase('application', 'zip')
    att.set_payload(zf.read())
    encoders.encode_base64(att)
    att.add_header('Content-Disposition', 'attachment', filename="mail.zip")

    fp=open(f,'rb')
      

    print "file reading"

            # att = email.mime.application.MIMEApplication(fp.read(),_subtype=subtype)
            # fp.close()
            # att.add_header('Content-Disposition','attachment',filename=filename)
    print "close file"
                
    msg.attach(att)

    print "attached attribute"
    print "came out of for"

    s = smtplib.SMTP('smtp.gmail.com')
    print "connected"
    s.starttls()

    print "Helloo mail sending"
    s.login('testemailmandrill@gmail.com','mandrill')
    s.sendmail(msg['From'],[msg['To']], msg.as_string())
    print "Email sent"
    s.quit()

    return render_template('upload.html',filenames=filenames)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # print send_from_directory(app.config['UPLOAD_FOLDER'],
                               # filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

if __name__ == '__main__':
    app.debug = True
    app.run()
    
