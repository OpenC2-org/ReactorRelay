#####################################################
#__________                      __                 #
#\______   \ ____ _____    _____/  |_  ___________  #
# |       _// __ \\__  \ _/ ___\   __\/  _ \_  __ \ #
# |    |   \  ___/ / __ \\  \___|  | (  <_> )  | \/ #
# |____|_  /\___  >____  /\___  >__|  \____/|__|    #
#        \/     \/     \/     \/                    #
#####################################################

# Django Imports
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

# Local Imports
from validators import openc2_validatior
from decorators import http_basic_auth
from forms import CreateActuator,CreateCapability
from profiles import Dispatcher
from models import Actuator,Capability,Job
import response

# Python Imports
import json

# Logging
import logging
logger = logging.getLogger("console")


# Create a single dispatcher on load
dispatcher = Dispatcher()

@csrf_exempt
@http_basic_auth
def service_router(request):

	"""
		Name: service_router
		Desc: Service router is the main view for the /openc2/ endpoint.
			  It's main purpose is to pass off jobs to the dispatcher
	"""

	if request.method != 'POST':
		
		logger.error("None POST request received.")

		return HttpResponse(status=400)

	else:

		try:

			# logger.debug(request.body)

			# Parse JSON into a dict			
			openc2_command = json.loads(request.body)
			
		except ValueError:

			# Not a valid JSON
			# TODO: Update to handle JAEN

			logger.error("Invalid JSON received from client %s" % request.META.get('REMOTE_ADDR'))
			return HttpResponse(status=400)

		# If this is a valid command
		if openc2_validatior(openc2_command):

			# Log the message
			logger.info("Inbound message received from %s" % request.META.get('REMOTE_ADDR'))
			logger.info("______________________")
			logger.info(request.body)
			logger.info("______________________")

			# If the user wants an out of band ack
			if "modifiers" in openc2_command:

				if "response" in openc2_command["modifiers"]:

					if openc2_command["modifiers"]["response"] == "ack":

						response.respond_ack(openc2_command["modifiers"])

			# Dispatch
			return dispatcher.dispatch(openc2_command,request.user)

		else:

			# We have no way to handle this type of command
			return HttpResponse(status=400)

		# TODO: Response - Gets here if the dispatcher hasnt responded for us
		return HttpResponse(status=200)
		
@login_required(login_url="login")
def home(request):

	"""
		Name: home
		Desc: main GUI
	"""
	# Forms for creating actuators and capabilities
	create_actuator_form = CreateActuator(request=request,prefix="create_host")
	create_capability_form = CreateCapability(request=request,prefix="create_capability")

	if request.method == "POST":

		if "delete_actuator_id" in request.POST:

			# Remove an actuator
			# TODO: Check cascade delete of capabilities

			try:

				Actuator.objects.get(pk=request.POST["delete_actuator_id"]).delete()

			except ObjectDoesNotExist, e:

				pass

		if "delete_capa_id" in request.POST:

			# Remove an individual capability
			try:

				Capability.objects.get(pk=request.POST["delete_capa_id"]).delete()

			except ObjectDoesNotExist, e:

				pass

		if "create_host-name" in request.POST:

			# Actuator creation
			create_actuator_form =  CreateActuator(request.POST,request=request,prefix="create_host")
			if create_actuator_form.is_valid():

				host = create_actuator_form.save()
				host.save()

		elif "create_capability-action" in request.POST:

			# Create a new capability for this relay

			create_capability_form = CreateCapability(request.POST,request=request,prefix="create_capability")

			if create_capability_form.is_valid():

				capability = create_capability_form.save()
				capability.save()

	# Get all actuators
	hosts = Actuator.objects.all()

	# Get all capabilities
	capabilities = Capability.objects.all()

	# Get all jobs
	jobs = Job.objects.all()

	# Count the number of python profiles the user has allowed us to link to capabilities
	profile_count = len(settings.OPENC2_PROFILES)

	# Get the relay name - stops multi-tabs getting confusing for the user
	my_name = settings.RELAY_NAME

	return render(request,"reactor_relay/home.html", {
		"create_actuator_form":create_actuator_form,
		"create_capability_form":create_capability_form,
		"profile_count":profile_count,
		"actuators":hosts,
		"jobs":jobs,
		"capabilities":capabilities,
		"relay_name":my_name,
		})