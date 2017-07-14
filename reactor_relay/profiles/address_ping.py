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
#	address_ping.py
#
# Descriptions: 
#	
#	Simple CLI ping of a given host from the local relay.
#

from reactor_relay.decorators import openc2_action
from django.conf import settings
from reactor_relay.profiles import Dispatcher
from reactor_relay.response import make_response_message,respond_message

import subprocess
import requests
import json
import os

# Cybox/STIX/TAXII Stuff
from cybox.core import Observable 
from cybox.objects.address_object import Address
# Logging
import logging
logger = logging.getLogger("console")

@openc2_action(actuator_list=[{"type":"process-network-scanner"}], target_list=[{"type":"cybox:AddressObjectType"}])
def scan(target, actuator, modifier):

	cybox_address_obs = Observable.from_json(json.dumps(target["specifiers"]))
	address = str(cybox_address_obs.object_.properties.address_value)

	result = icmp_ping(address)

	if "respond-to" in modifier:
		if "command-ref" in modifier:
			ref=modifier["command-ref"]
		else:
			ref=None

		respond_message(make_response_message(ref, "simple", {"address":address,"ping":result}), modifier["respond-to"])

	return True
	
def icmp_ping(address):

	# Returns True on up, False on down
	if os.system("/bin/ping -c 3 %s" % (address)) == 0:

		return True

	else:

		return False
