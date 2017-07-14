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
#	uri_virustotal_lookup.py
#
# Descriptions: 
#	
#	VirusTotal lookup of a given uri from the local relay.
#

from reactor_relay.decorators import openc2_action
from django.conf import settings
from reactor_relay.profiles import Dispatcher
from reactor_relay.response import make_response_message,respond_message

import subprocess
import requests
import json
import os
from virus_total_apis import PublicApi

# Cybox/STIX/TAXII Stuff
from cybox.core import Observable 
# Logging
import logging
logger = logging.getLogger("console")

API_KEY = "c2a0649b96ea22e0e1c4da3496644617f4571293ae3539dee1c1488a1a24abad"

@openc2_action(actuator_list=[{"type":"process-reputation-service"}], target_list=[{"type":"cybox:URIObjectType"}])
def scan(target, actuator, modifier):

	cybox_address_obs = Observable.from_json(json.dumps(target["specifiers"]))
	uri = str(cybox_address_obs.object_.properties.value)

	result = virus_total_scan(uri)

	if "respond-to" in modifier:
		if "command-ref" in modifier:
			ref=modifier["command-ref"]
		else:
			ref=None

		respond_message(make_response_message(ref, "simple", {"uri":uri,"virus_total":result}), modifier["respond-to"])

	return True
	
def virus_total_scan(uri):

	vt = PublicApi(API_KEY)

	response = vt.get_url_report(uri)

	print response


