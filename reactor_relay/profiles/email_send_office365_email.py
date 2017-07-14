#####################################################
#__________                      __                 #
#\______   \ ____ _____    _____/  |_  ___________  #
# |       _// __ \\__  \ _/ ___\   __\/  _ \_  __ \ #
# |    |   \  ___/ / __ \\  \___|  | (  <_> )  | \/ #
# |____|_  /\___  >____  /\___  >__|  \____/|__|    #
#        \/     \/     \/     \/                    #
#####################################################
# Name: 
#	
#	email_send_office365_email.py
#
# Descriptions: 
#	
#	Send Office365 email from the local relay.
#

from reactor_relay.decorators import openc2_action
from django.conf import settings
from reactor_relay.profiles import Dispatcher
from reactor_relay.response import make_response_message,respond_message

import subprocess
import requests
import json
import os
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

# Cybox/STIX/TAXII Stuff
from cybox.core import Observable 

# Logging
import logging
logger = logging.getLogger("console")


@openc2_action(actuator_list=[{"type":"process-email-service"}], target_list=[{"type":"cybox:EmailMessageObjectType"}])
def notify(target, actuator, modifier):

	cybox_address_obs = Observable.from_json(json.dumps(target["specifiers"]))
	send_from = str(cybox_address_obs.object_.properties.from_.address_value)
	# send_to only sends to the first email address
	send_to = str(cybox_address_obs.object_.properties.to[0])
	subject = str(cybox_address_obs.object_.properties.subject)
	message = str(cybox_address_obs.object_.properties.raw_body)

	result = send_mail(send_from, send_to, subject, message)

	if "respond-to" in modifier:
		if "command-ref" in modifier:
			ref=modifier["command-ref"]
		else:
			ref=None

		respond_message(make_response_message(ref, "simple", {"subject":subject,"sent":result}), modifier["respond-to"])

	return True
	
def send_mail(send_from, send_to, subject, message):
	username = "support@zepko.com"
	password = "a5mGxYTYWo"
	server="smtp.office365.com"
	port=587
	msg = MIMEMultipart('related')
	msg['From'] = send_from
	msg['To'] = send_to 
	msg['Subject'] = subject
	msg.attach( MIMEText(text, 'plain') )
	smtp = smtplib.SMTP(server, port)
	smtp.login(username, password)
	smtp.sendmail(send_from, send_to, msg.as_string())
	smtp.close()
	return True
	
