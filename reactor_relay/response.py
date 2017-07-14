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
#	responder.py
#
# Descriptions: 
#	
#	Holds all logic for handling responses - WORK IN PROGRESS - THIS IS JUST AN EXAMPLE
#

from django.conf import settings
import requests
import json

# Logging
import logging
logger = logging.getLogger("console")

# These will change at somepoint, so putting them in variables for now
command_respond_to_identifier = "respond_to"


def make_response_message(command_ref, com_type, value):

	"""
		Name: make_response_message
		Desc: This is used to take a dictionary value and create a response OpenC2 command
		Args:
				command_ref - ID to associate the message to a previous command
				com_type - simple/ack
				value - dict to send back (use this for data)
	"""
	msg = {}

	msg["action"] = "response"

	msg["target"] = {}
	msg["target"]["type"] = "openc2:Data"

	msg["modifiers"] = {}

	msg["modifiers"]["command-ref"] = command_ref
	msg["modifiers"]["type"] = com_type
	msg["modifiers"]["value"] = value


	return json.dumps(msg)

def respond_ack(modifiers):

	"""
		Name: respond_ack
		Desc: Sends an ACK to an upstream orchestrator
		Args:
				modifiers - OpenC2 modifiers section as a dict				
 	"""
 	try:

		if "id" in modifiers and command_respond_to_identifier in modifiers and "response" in modifiers:

			logger.info("Responding to message ref:%s to %s [ACK]" % (modifiers["id"],modifiers["respond_to"]))

			message_to_send = make_response_message(modifiers["id"],"ack","ack")

			r = requests.post(modifiers["respond_to"], message_to_send)

			if r.status_code == 200:

				logger.info("Successful ACK sent to %s command ref: %s." % (modifiers["respond_to"],modifiers["id"]))

			else:

				logger.error("Failed to send ACK to %s command ref: %s." % (modifiers["respond_to"],modifiers["id"]))

		else:

			logger.error("A response was requested, but didnt have the required fields to facilate response.")

	except Exception,e:

		logger.error("Failed to respond to upstream caller, an exception occured: %s" % str(e))

def respond_message(message,respond_to_url):

	"""
		Name: respond_message
		Desc: Sends a complete OpenC2 RESPONSE message to a URL
		Args:
			  message - OpenC2 modifiers section as a dict				
 	"""
 	try:
		logger.info("Send message %s to %s" % (message,respond_to_url))
		req = requests.post(respond_to_url, data=message, verify=False)
	except Exception,e:

		logger.error("Failed to respond to upstream caller, an exception occured: %s" % str(e))