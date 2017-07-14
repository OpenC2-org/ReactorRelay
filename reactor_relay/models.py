#####################################################
#__________                      __                 #
#\______   \ ____ _____    _____/  |_  ___________  #
# |       _// __ \\__  \ _/ ___\   __\/  _ \_  __ \ #
# |    |   \  ___/ / __ \\  \___|  | (  <_> )  | \/ #
# |____|_  /\___  >____  /\___  >__|  \____/|__|    #
#        \/     \/     \/     \/                    #
#####################################################
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
import json

# Logging
import logging
logger = logging.getLogger("console")

class OpenC2Action(object):

	"""
	Name: OpenC2Action
	Desc: This is used more as a profile decorator, it never gets stored in the database.
		  The main functionality is to create signatures for profiles, and then identify new
		  messages against the profile to see if it is capable of actionin the OpenC2 command.
	"""

	def __init__(self,name):

		self.name = name
		self.function_signatures = []
		self.function = None


	def sig_match(self, message, function_signature):

		# Should work to the following logic:
		#							|    Specifier In Profile Signature	  |    Specifier Not In Profile Signature 
		# Specifier In message		|			  Match					  |				Match - Generic Profile - But use profile logic to check specifiers (saves writing a profile for every firewall etc)
		# Specifier Not In message	|			  No Match   			  |				Match
		

		# Check actions
		if function_signature["action"] != message["action"]:

			return False

		# Check Targets
		if function_signature["target"]["type"] != message["target"]["type"]:

			return False

		if "specifiers" in function_signature["target"]:

			for target_spec in function_signature["target"]["specifiers"]:

				if target_spec in message["target"]["specifiers"]:

					if function_signature["target"]["specifiers"][target_spec] != message["target"]["specifiers"][target_spec]:

						return False

				else:

					return False
		
		# Check Actuators
		if "actuator" in function_signature:

			if function_signature["actuator"]["type"] != message["actuator"]["type"]:

				return False

			if "specifiers" in function_signature["actuator"]:

				for actuator_spec in function_signature["actuator"]["specifiers"]:

					if actuator_spec in message["actuator"]["specifiers"]:

						if function_signature["actuator"]["specifiers"][actuator_spec] != message["actuator"]["specifiers"][actuator_spec]:

							return False
					else:
						return False
		return True

	def identify(self, message):

		# Identify functions capable of handling this message

		for func_sig in self.function_signatures:

			if self.sig_match(message,func_sig["sig"]):

				logger.info("A %s profile matched signature %s" % (self.name,json.dumps(func_sig["sig"])))

				return True

		return False


	def register(self, sig, function):

		self.function_signatures.append({"sig":sig,"function":function})
		self.function = function

	def __call__(self,target, actuator, modifier):

		return self.function(target, actuator, modifier)


class Actuator(models.Model):

	# Freindly name for the host
	name = models.CharField(max_length=200,unique=True)

	# OpenC2 Actuator type - eg. network-ids
	openc2_type = models.CharField(max_length=200)

	# IP to run managment commands from
	ip = models.CharField(max_length=15)

	# Creds for performing the action
	username = models.CharField(max_length=200,null=True,blank=True)
	password = models.CharField(max_length=200,null=True,blank=True)

class CybOXType(models.Model):

	#Cybox identifier
	identifier = models.CharField(max_length=50)

class Capability(models.Model):

	# Descriptor
	name = models.CharField(max_length=200)

	# Actuator
	actuators = models.ManyToManyField(Actuator)

	# Openc2 action - eg. DENY
	action = models.CharField(max_length=50)

	# Requires what type of cybox object
	requires = models.ForeignKey(CybOXType,null=False,blank=False)

	# Which profile executes this code
	profile = models.CharField(max_length=200)

class JobStatus(models.Model):

	status = models.CharField(max_length=40)

class Job(models.Model):

	# Linked capability this job leverages
	capability = models.ForeignKey(Capability)

	# JSON OpenC2 command
	raw_message = models.TextField(max_length=5000)

	# Time we received the job
	created_at = models.DateTimeField(default=timezone.now, blank=True)

	# Upstream details
	upstream_respond_to = models.CharField(max_length=5000, null=True)
	upstream_command_ref = models.CharField(max_length=100, null=True)

	# Job status
	status = models.ForeignKey(JobStatus)

	# User acountability
	created_by = models.ForeignKey("auth.User")