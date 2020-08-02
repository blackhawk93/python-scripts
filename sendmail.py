#This script will help in sending bulk emails using sendmail. As long as the content remains the same you can add a list of email addresses from a file and this script will deliver it to all of them. Destination mail server must have port 25 open.

import smtplib

f = open("/home/ian/Documents/mails.txt")    #Path of your file with emails
mails = f.readlines()
mylist = []

for emails in mails:	#This loop will convert your file to a comma seperated list

	mylist.append(emails.rstrip())

SERVER = "10.10.10.197"		#Server IP listening on port 25

FROM = "blackhawk@sneakymail.htb"	#Anything as sender
TO = mylist
SUBJECT = "Hello"
TEXT = "You can ping me on http://10.10.14.29"	#Enter any Text as the body

message = """\
From: %s
To: %s
Subject: %s

%s
""" % (FROM, ", ".join(TO), SUBJECT, TEXT)

server = smtplib.SMTP(SERVER)
server.sendmail(FROM, TO, message)
server.quit()


