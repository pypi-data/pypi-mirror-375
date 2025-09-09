"""
Email utility functions.
Copyright (C) 2022 Humankind Investments
"""

import os, re
import traceback
import numpy as np

from datetime import date
from dateutil.parser import parse

import smtplib
import imaplib
from email import message_from_bytes
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


def send_email(content, subject, receiver, credentials, importance_level=None):
    """
    Send an email alert.

    Parameters
    ----------
    content : str
        Content of the email to send.
    subject : str
        Subject of the email to send.
    receiver : str
        Email to send the alert to.
    credentials : dict
        Provides the credentials for sender, password, and port.
    importance_level : str, optional
        The importance flag of the email. The default is None.
    """
    
    for key in ['sender', 'password', 'port']:
        assert key in credentials, f"credentials must have a key for {key}"
    
    sender = credentials['sender']
    passw = credentials['password']
    port = credentials['port']
    
    msg = MIMEText(content)
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    msg.add_header('Content-Type', 'text/html')

    if importance_level: msg.add_header('Importance', importance_level)

    server = smtplib.SMTP('smtp.' + sender.split('@')[1], port)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(sender, passw)
    server.send_message(msg)
    server.quit()


def wrotetoday(platform, receivers, content, credentials):
    """
    Send an email notification that a script succeeded.

    Parameters
    ----------
    platform : str
        Name of the platform.
    receivers : list of str
        List of emails to send the alert to.
    content : str
        Content of the email alert.
    credentials : dict
        Provides the credentials for sender, password, and port.
    """
    
    subject = '[%s] finished writing %s' % (platform, date.today())

    if isinstance(receivers, list):
        receivers= ", ".join(receivers)
        send_email(content, subject, receivers, credentials)
    elif isinstance(receivers, str):
        send_email(content, subject, receivers, credentials)
    else:
        raise TypeError("receivers must be a str or list")

            
def error_alert(platform, receivers, filename, credentials, e=None):
    """
    Send an email alert that a script failed.

    Parameters
    ----------
    platform : str
        Name of the platform to be included in the subject line.
    receivers : list of str
        List of emails to send the alert to.
    filename : str
        Name of the script which ran into the error.
    credentials : dict
        Provides the credentials for sender, password, and port.
    e : Exception
        The exception that was raised.
    """
    
    subject = '[ERROR] %s failed %s' % (platform, date.today())
    if e is None:
        error = """No error message was provided. Include Exception in the 
        call to error_alert to include the error message."""
    else:
        error = ''.join(traceback.format_exception(None, e, e.__traceback__)).replace('    ', '&emsp;').replace(
                                '  ', '&ensp;').replace('\n', '<br>')
    content = f"""{filename} ran into the following error: <br> 
                  <span style="font-family: Courier;">{error}</span><br>
                  Check log for further details.
               """
    importance_level = 'High'
    if isinstance(receivers, list):
        receivers= ", ".join(receivers)
    elif isinstance(receivers, str):
        pass
    else:
        raise TypeError("receivers must be a str or list")
    
    send_email(content, subject, receivers, credentials, importance_level)


def send_email_with_attachment(content, subject, receiver, credentials, attachment_paths):
    """
    Send an email alert.

    Parameters
    ----------
    content : str
        Content of the email to send.
    subject : str
        Subject of the email to send.
    receiver : str
        Email to send the alert to.
    credentials : dict
        Provides the credentials for sender, password, and port.
    attachment_paths : list
        List of file path(s) for the attachment(s)
    """
    
    for key in ['sender', 'password', 'port']:
        assert key in credentials, f"credentials must have a key for {key}"
    
    if not isinstance(attachment_paths, list):
        attachment_paths= [attachment_paths]
        
    sender = credentials['sender']
    passw = credentials['password']
    port = credentials['port']
    
    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(content, _subtype='html'))
    msg.add_header('Content-Type', 'text/html')
        
    for path in attachment_paths:
        # Get the file name
        attachment_name = os.path.basename(path)
    
        # Read the attachment file
        with open(path, "rb") as file:
            attachment_part = MIMEApplication(
                file.read(),
                Name=attachment_name
            )
        attachment_part.add_header(
            "Content-Disposition",
            f"attachment; filename= {attachment_name}",
        )
    
        # Add the attachment to the message
        msg.attach(attachment_part)

    with smtplib.SMTP('smtp.' + sender.split('@')[1], port) as server:
        server.starttls()
        server.login(sender, passw)
        server.send_message(msg)


def download_attachments(response, folder_name, get_attachment=True):
    """
    Download the attachments from an email and save it to the given folder.

    Parameters
    ----------
    response : tuple
        Component of an email message, i.e. message envelope and data.
    folder_name : str
        The folder path in which to save the attachments.
    get_attachment : bool
        Get attachments if they exist. Otherwise, download email body.

    Returns
    -------
    str
        The names to which to save the files, excluding the path.
    """
    
    filenames = []
    if isinstance(response, tuple):
        # parse a bytes email into a message object
        msg = message_from_bytes(response[1])
        
        # decode the email subject
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes): subject = subject.decode(encoding)  # decode bytes to str
        subject = re.sub(r':', '', ' '.join(subject.split()))

        # if the email message is multipart
        if msg.is_multipart():
            # iterate over email parts
            for part in msg.walk():
                # download and save attachment if it exists
                content_disposition = str(part.get('Content-Disposition'))
                if 'attachment' in content_disposition and get_attachment:
                    filename = part.get_filename()
                    if filename:
                        filepath = os.path.join(folder_name, filename)
                        if not os.path.exists(folder_name): os.makedirs(folder_name)
                        with open(filepath, "wb") as f: f.write(part.get_payload(decode=True))
                        filenames.append(filename)
            # if no attachment found, iterate over email parts again and get plain text
            if not filenames:
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain':
                        filename = subject + '.txt'
                        filepath = os.path.join(folder_name, filename)
                        if not os.path.exists(folder_name): os.makedirs(folder_name)
                        with open(filepath, 'wb') as f: f.write(part.get_payload(decode=True))
                        filenames.append(filename)
        else:
            # extract content type and body of email
            content_type = msg.get_content_type()
            body = msg.get_payload(decode=True).decode()

            if content_type == 'text/html' or content_type == 'text/plain':
                if content_type == 'text/html': ext = '.html'
                elif content_type == 'text/plain': ext = '.txt'
                filename = subject + ext
                filepath = os.path.join(folder_name, filename)
                if not os.path.exists(folder_name): os.makedirs(folder_name)
                with open(filepath, "w") as f: f.write(body)
                filenames.append(filename)

    return filenames


def readmails(username, password, tag, folder_name, sender,
              n_mails=np.inf, min_date='', get_attachment=True):
    """
    Download the attachments from the most recent emails with the desired tag.

    Parameters
    ----------
    username : str
        Email address from which to read messages.
    password : str
        Email password.
    tag : str
        A tag to identify messages in the inbox.
    folder_name : str
        The path of the folder to which to save the attachment.
    sender : str
        The email address of the desired sender. Emails from other senders will
        be excluded from the potential emails to read.
    n_mails : int
        The number of recent emails to read. Default reads all emails.
    min_date : str
        The minimum date on or after which to check for emails. Default checks all dates.
    get_attachment : bool
        Get attachments if they exist. Otherwise, download email body.

    Returns
    -------
    list
        List of file names, excluding the path.
    """

    # create an IMAP4 class with SSL
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(username, password)

    # get total number of messages
    status, messages = imap.select(tag)
    messages = int(messages[0])

    # loop over relevant messages and select emails of interest
    datetimeorder = {}
    for p in range(messages, 0, -1):
        res, msg = imap.fetch(str(p), "(RFC822)")
        if res != 'OK': continue
        email_message = message_from_bytes(msg[0][1])
        email_from = email_message['From'].lower()
        pat = r'[^\s<]+@[^\s>]+'
        if re.findall(pat, email_from)[0] != sender.lower(): continue
        datetime_obj = parse(email_message['Date'])
        datetimeorder.update({(email_message['Subject'], datetime_obj) : p})
        if len(datetimeorder) >= n_mails or str(datetime_obj.date()) < min_date: break
    
    # get recent emails and download attachments
    filenamelst = []
    for index in datetimeorder.values():
        res, msg = imap.fetch(str(index), '(RFC822)')
        for response in msg:
            filenames = download_attachments(response, folder_name, get_attachment)
            if filenames:
                for filename in filenames: filenamelst.append(filename)
    
    return filenamelst

