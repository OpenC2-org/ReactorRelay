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
#	response.py
#
# Descriptions: 
#	
#	This profile is a basic response receiver, it just reveives and logs responses
#
#
# Sample Files
#	
#	- ./samples/response_ack.json

from reactor_relay.decorators import openc2_action
from django.conf import settings

# Logging
import logging
logger = logging.getLogger("console")

@openc2_action(target_list=[{"type":"openc2:Data"}])
def response(target, actuator, modifier):

	if "command-ref" in modifier and "type" in modifier:

		if "value" in modifier:
		
			logger.info("Response message received: command:%s type:%s value:%s" % (modifier["command-ref"],modifier["type"],modifier["value"]))
		
		else:

			logger.info("Response message received: command:%s type:%s " % (modifier["command-ref"],modifier["type"]))
	else:

		logger.warning("RESPONSE Message received that was missing the correct command-ref / type feilds")
