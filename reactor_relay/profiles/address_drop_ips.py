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
#	address_drop_ips.py
#
# Descriptions: 
#	
#	Issuse an IPtables drop rule for an IP on a linux box via SSH
#

from reactor_relay.decorators import openc2_action
from django.conf import settings
from reactor_relay.profiles import Dispatcher
from reactor_relay.response import make_response_message,respond_message
from reactor_relay.models import Actuator
import subprocess
import requests
import json
import os
import paramiko 

# Cybox/STIX/TAXII Stuff
from cybox.core import Observable 
from cybox.objects.address_object import Address
# Logging
import logging
logger = logging.getLogger("console")

@openc2_action(actuator_list=[{"type":"network-ips"}], target_list=[{"type":"cybox:AddressObjectType"}])
def deny(target, actuator, modifier):

	cybox_address_obs = Observable.from_json(json.dumps(target["specifiers"]))
	address = str(cybox_address_obs.object_.properties.address_value)

	result_message = {}

	if "specifiers" in actuator:
	
		# Handling for specific devices - lookup on name or id
		if "name" in actuator["specifiers"]:

			actuator = Actuator.objects.get(name=actuator["specifiers"]["name"])
			result_message[actuator.name] = drop_address(address,actuator)

		elif "id" in actuator["specifiers"]:

			actuator = Actuator.objects.get(pk=actuator["specifiers"]["id"])
			result_message[actuator.name] = drop_address(address,actuator)

	else:
		
		for actuator in Actuator.objects.filter(openc2_type="network-ips"):

			result_message[actuator.name] = drop_address(address,actuator)

	if "respond-to" in modifier:
		if "command-ref" in modifier:
			ref=modifier["command-ref"]
		else:			
			ref=None

		respond_message(make_response_message(ref, "simple", {"address":address,"result":result_message}), modifier["respond-to"])

	return True

@openc2_action(actuator_list=[{"type":"network-ips"}], target_list=[{"type":"cybox:AddressObjectType"}])
def allow(target, actuator, modifier):

	cybox_address_obs = Observable.from_json(json.dumps(target["specifiers"]))
	address = str(cybox_address_obs.object_.properties.address_value)

	result_message = {}

	if "specifiers" in actuator:
	
		# Handling for specific devices - lookup on name or id
		if "name" in actuator["specifiers"]:

			actuator = Actuator.objects.get(name=actuator["specifiers"]["name"])
			result_message[actuator.name] = allow_address(address,actuator)

		elif "id" in actuator["specifiers"]:

			actuator = Actuator.objects.get(pk=actuator["specifiers"]["id"])
			result_message[actuator.name] = allow_address(address,actuator)

	else:
		
		for actuator in Actuator.objects.filter(openc2_type="network-ips"):

			result_message[actuator.name] = allow_address(address,actuator)

	if "respond-to" in modifier:
		if "command-ref" in modifier:
			ref=modifier["command-ref"]
		else:			
			ref=None

		respond_message(make_response_message(ref, "simple", {"address":address,"result":result_message}), modifier["respond-to"])
	
	return True

def drop_address(address,actuator):

	try:

		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
		ssh.connect(actuator.ip, username=actuator.username, password=actuator.password)

		result = {}
		result["run"] = True

		stdin, stdout, stderr = ssh.exec_command("iptables -I FORWARD -d %s -j DROP" % (address))
		
		result["stdout"] = str(stdout.read())
		result["stderr"] = str(stderr.read())
 
		return result
		
	except Exception,e:

		result = {}

		result["run"] = False
		result["error"] = str(e)

		return result


def allow_address(address,actuator):

	try:

		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
		ssh.connect(actuator.ip, username=actuator.username, password=actuator.password)

		result = {}
		result["run"] = True

		stdin, stdout, stderr = ssh.exec_command("iptables -D FORWARD -d %s -j DROP" % (address))
		
		result["stdout"] = str(stdout.read())
		result["stderr"] = str(stderr.read())
 
		return result

	except Exception,e:

		result = {}

		result["run"] = False
		result["error"] = str(e)

		return result