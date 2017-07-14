#####################################################
#__________                      __                 #
#\______   \ ____ _____    _____/  |_  ___________  #
# |       _// __ \\__  \ _/ ___\   __\/  _ \_  __ \ #
# |    |   \  ___/ / __ \\  \___|  | (  <_> )  | \/ #
# |____|_  /\___  >____  /\___  >__|  \____/|__|    #
#        \/     \/     \/     \/                    #
#####################################################

# Python Imports
import collections
import imp
import os
import json

# Django Imports
from django.http import Http404
from django.http import HttpResponse
from django.conf import settings

# Local Imports
from ..models import OpenC2Action,Capability,Actuator,Job,JobStatus

# Logging
import logging
logger = logging.getLogger("console")

class Dispatcher(object):


	def __init__(self):
		"""
		Name: Dispatcher
		Desc: On creation this loads the profiles from the config file and loads them as a module
			  This allows users to hard disable capabilities quickly
		"""

		logger.info("Initialising dispatcher")
		
		self.profiles = collections.deque()

		for module in settings.OPENC2_PROFILES:

			logger.info("Loading profile %s" % module)
			self.profiles.appendleft(imp.load_source(module.split(".")[0], "./reactor_relay/profiles/"+module))

	def capabilities(self):

		"""
		Name: capabilities
		Desc: 	This is used to generate a list of capabilities for this relay
				This tells the upstream orchestrator what this relay is capable of
		"""

		logger.debug("Capabilities called. Upstream is syncing")
		
		# # New method - uses defined capabilities
		# registered_actuators = []
		info = []

		registered_capabilities = []

		# For all of my capabilities:
		for capa in Capability.objects.all():

			# For each type of host capable
			actuator_types = {}
			for actuator in capa.actuators.all():

				# For each type of actuator they require
				if actuator.openc2_type in actuator_types:
					
					actuator_types[actuator.openc2_type].append(actuator)

				else:

					actuator_types[actuator.openc2_type] = []
					actuator_types[actuator.openc2_type].append(actuator)

				# Create description
				for a_type in actuator_types:

					supported_hosts = []
					for host in actuator_types[a_type]:

						supported_hosts.append({"id":host.id,"name":host.name,"action_tag":capa.name})

					capa_dict = {"action":capa.action,"actuator":{"type":a_type,"specifiers":{"available":supported_hosts}},"target":{"type":capa.requires.identifier}}
					info.append(capa_dict)

		return json.dumps(info)


	def dispatch(self,message,user):
		
		"""
		Name: dispatch
		Desc: Dispatcher takes a dict version of an OpenC2 command and works out which capabilites can execute it
		"""

		logger.debug("Dispatcher called")

		# Check action / target type

		# Query openc2:openc2 calls a capabilities lising
		if message["action"] == 'query' and message["target"]["type"] == 'openc2:openc2':
			return HttpResponse(self.capabilities(),status=200)

		# Force all actions into lower case so we dont need to worry about standardising profile code
		message['action'] = message['action'].lower()

		# New method - uses defined capabilities to work out if we can handle this

		# If specifiers - otherwise handle generely

		if "specifiers" in message["actuator"]:
			try:
				if "id" in message["actuator"]["specifiers"]:

					# Lookup on id
					requested_actuator = Actuator.objects.get(pk=message["actuator"]["specifiers"]["id"])

					capabilities = Capability.objects.filter(action=message['action'],requires__identifier=message["target"]["type"],actuators=requested_actuator)

				elif "name" in message["actuator"]["specifiers"]:

					# Lookup on name
					requested_actuator = Actuator.objects.get(name=message["actuator"]["specifiers"]["name"])
					capabilities = Capability.objects.filter(action=message['action'],requires__identifier=message["target"]["type"],actuators=requested_actuator)

				else:

					raise ObjectDoesNotExist
					
			except ObjectDoesNotExist,e:

				# Fall back to general
				capabilities = Capability.objects.filter(action=message['action'],requires__identifier=message["target"]["type"])

		else:

			capabilities = Capability.objects.filter(action=message['action'],requires__identifier=message["target"]["type"])

		# Now identify if we can handle this message
		for capa in capabilities:

			loaded_profile = imp.load_source(capa.profile.split(".")[0], "./reactor_relay/profiles/"+capa.profile)
			f = getattr(loaded_profile, message['action'], None)
			if f:

				if f.identify(message):

					# Create Job
					new_job = Job(capability=capa,
						raw_message=json.dumps(message,sort_keys=True,indent=4).replace("\t", u'\xa0\xa0\xa0\xa0\xa0'),
						status=JobStatus.objects.get(status="Pending"),
						created_by=user)

					if "command-ref" in message["modifiers"] and "respond-to" in message["modifiers"]:

						new_job.upstream_respond_to = message["modifiers"]["respond-to"]
						new_job.upstream_command_ref = message["modifiers"]["command-ref"]

					new_job.save()

					status = f(message["target"], message.get("actuator"), message.get("modifiers"))

					# Set Job Status based on success
					if status:

						new_job.status = JobStatus.objects.get(status="Success")

					else:

						new_job.status = JobStatus.objects.get(status="Failed")

					new_job.save()

					# 200's are I have received this message - not the message executed correctly
					# If you need to catch errors - the upstream should request a response
					return HttpResponse(status=200)
				
				else:

					# Linked profile code cant perform this action
					return HttpResponse(status=501)
			
			else:

				# If i dont have the capability
				return HttpResponse(status=501)



				

