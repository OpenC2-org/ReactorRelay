#####################################################
#__________                      __                 #
#\______   \ ____ _____    _____/  |_  ___________  #
# |       _// __ \\__  \ _/ ___\   __\/  _ \_  __ \ #
# |    |   \  ___/ / __ \\  \___|  | (  <_> )  | \/ #
# |____|_  /\___  >____  /\___  >__|  \____/|__|    #
#        \/     \/     \/     \/                    #
#####################################################

from django import forms
from models import Actuator,Capability,CybOXType
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings

# Note - this is not a complete list - this is a list of MSSP viable actuators
openc2_actuators = (("endpoint-workstation","endpoint-workstation"),
("endpoint-server","endpoint-server"),
("endpoint-laptop","endpoint-laptop"),
("endpoint-smart-phone","endpoint-smart-phone"),
("endpoint-tablet","endpoint-tablet"),
("endpoint-printer","endpoint-printer"),
("endpoint-smart-meter","endpoint-smart-meter"),
("endpoint-pos-terminal","endpoint-pos-terminal"),
("endpoint-digital-telephone-handset","endpoint-digital-telephone-handset"),
("endpoint-sensor","endpoint-sensor"),
("network","network"),
("network-firewall","network-firewall"),
("network-router","network-router"),
("network-ids","network-ids"),
("network-hub","network-hub"),
("network-bridge","network-bridge"),
("network-switch","network-switch"),
("network-modem","network-modem"),
("network-wap","network-wap"),
("network-gateway","network-gateway"),
("network-proxy","network-proxy"),
("network-nic","network-nic"),
("network-vpn","network-vpn"),
("network-guard","network-guard"),
("network-sensor","network-sensor"),
("network-hips","network-hips"),
("network-ips","network-ips"),
("network-security-manager","network-security-manager"),
("network-sense-making","network-sense-making"),
("process","process"),
("process-vulnerability-scanner","process-vulnerability-scanner"),
("process-network-scanner","process-network-scanner"),
("process-connection-scanner","process-connection-scanner"),
("process-anti-virus-scanner","process-anti-virus-scanner"),
("process-file-scanner","process-file-scanner"),
("process-aaa-server","process-aaa-server"),
("process-virtualization-service","process-virtualization-service"),
("process-sandbox","process-sandbox"),
("process-dns-server","process-dns-server"),
("process-email-service","process-email-service"),
("process-directory-service","process-directory-service"),
("process-remediation-service","process-remediation-service"),
("process-reputation-service","process-reputation-service"),
("process-location-service","process-location-service"))

# Actions
openc2_actions = (("SCAN","SCAN"),
("LOCATE","LOCATE"),
("QUERY","QUERY"),
("REPORT","REPORT"),
("GET","GET"),
("NOTIFY","NOTIFY"),
("DENY","DENY"),
("CONTAIN","CONTAIN"),
("ALLOW","ALLOW"),
("START","START"),
("STOP","STOP"),
("RESTART","RESTART"),
("PAUSE","PAUSE"),
("RESUME","RESUME"),
("CANCEL","CANCEL"),
("SET","SET"),
("UPDATE","UPDATE"),
("MOVE","MOVE"),
("REDIRECT","REDIRECT"),
("DELETE","DELETE"),
("SNAPSHOT","SNAPSHOT"),
("DETONATE","DETONATE"),
("RESTORE","RESTORE"),
("SAVE","SAVE"),
("MODIFY","MODIFY"),
("THROTTLE","THROTTLE"),
("DELAY","DELAY"),
("SUBSTITUTE","SUBSTITUTE"),
("COPY","COPY"),
("SYNC","SYNC"),
("DISTILL","DISTILL"),
("AUGMENT","AUGMENT"),
("INVESTIGATE","INVESTIGATE"),
("MITIGATE","MITIGATE"),
("REMEDIATE","REMEDIATE"),
("RESPONSE","RESPONSE"),
("ALERT","ALERT"))

class ActuatorChoice(forms.ModelChoiceField):
	def label_from_instance(self,obj):
		return "%s" % (obj.name)

class CyboxChoice(forms.ModelChoiceField):
	def label_from_instance(self,obj):
		return "%s" % (obj.identifier)

class ActuatorSelect(forms.ModelMultipleChoiceField):
	def label_from_instance(self,obj):
		return "%s" % (obj.name)


class CreateActuator(forms.ModelForm):

	openc2_type = forms.ChoiceField(choices=openc2_actuators)
	password = forms.CharField(widget=forms.PasswordInput())
	class Meta:
		model = Actuator
		exclude = []

	def __init__(self, *args, **kwargs):

		self.request = kwargs.pop('request', None)
		super(CreateActuator, self).__init__(*args, **kwargs)
		
		for visible in self.visible_fields():
			visible.field.widget.attrs['class'] = 'form-control'

class LoginForm(AuthenticationForm):
	username = forms.CharField(label="Username", max_length=30, 
							   widget=forms.TextInput(attrs={'class': 'form-control',
							   								 'name': 'username'}))

	password = forms.CharField(label="Password", max_length=30, 
							   widget=forms.PasswordInput(attrs={'class': 'form-control',
							   									 'name': 'password'}))

class CreateCapability(forms.ModelForm):

	action = forms.ChoiceField(choices=openc2_actions)

	active_profiles = []

	# We show all of these - because their selection is handled in JS+ if we need it
	actuators = ActuatorSelect(
        queryset=Actuator.objects.all(),
        widget=forms.SelectMultiple(),
        required=True
    )

	requires = CyboxChoice(queryset=CybOXType.objects.all(), empty_label=None)

	for p in settings.OPENC2_PROFILES:

		active_profiles.append((p,p))

	profile = forms.ChoiceField(choices=active_profiles)

	class Meta:
		model = Capability
		exclude = []

	def __init__(self, *args, **kwargs):

		self.request = kwargs.pop('request', None)
		super(CreateCapability, self).__init__(*args, **kwargs)
		
		for visible in self.visible_fields():
			visible.field.widget.attrs['class'] = 'form-control'
