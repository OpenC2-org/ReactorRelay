#####################################################
#__________                      __                 #
#\______   \ ____ _____    _____/  |_  ___________  #
# |       _// __ \\__  \ _/ ___\   __\/  _ \_  __ \ #
# |    |   \  ___/ / __ \\  \___|  | (  <_> )  | \/ #
# |____|_  /\___  >____  /\___  >__|  \____/|__|    #
#        \/     \/     \/     \/                    #
#####################################################

from jsonschema import validate

def openc2_validatior(openc2_message):

	schema = {
		"type" : "object",
		"properties" : {
			"action": {"type":"string"},
			"target":{
					"type" : "object",
					"properties":{
						"type":{"type":"string"},
						"specifiers":{
								"type":"object",
								"properties":{},
								"additionalProperties": True,
								}
					},
					"required": ["type"],
			},
			"actuator":{
					"type" : "object",
					"properties":{
						"type":{"type":"string"},
						"specifiers":{
								"type":"object",
								"properties":{},
								"additionalProperties": True,
								}
					},
					"required": ["type"]
					
			},
			"modifiers":{
					"type":"object",
					"properties":{},
					"additionalProperties": True,
			}
		
		},
		"required": ["action","target"]
	}

	try:

		validate(openc2_message,schema)
		return True
	
	except Exception, e:

		return False
