from settings import TIMEZONE, LANGUAGE

"""
This file contains the tools that are used by the main controller.
Tools:
    conversation
    set_alarm
    what_time
    set_volume
"""

tools = [
    {
        "type": "function",
        "function": {
            "name": "conversation",
            "description": "If no other tool is called, this tool should be called. It should be able to have a conversation with the user, should comment and ask about the user context. Keep it informal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string", 
                        "description": "The reply, question or comment about the user input. Don't try to force the user to do something. Keep it informal and use the language " + LANGUAGE
                    },
                    "module": {
                        "type": "string", 
                        "enum": ["general"]
                    },
                    "error_message": {
                        "type": "string", 
                        "description": "The message alerting that there has been an issue with the action, the language used should be "  + LANGUAGE
                    },
                    "conversation_mode": {
                        "type": "boolean", 
                        "description": "If the conversation needs a reply from the user, like ending in a question, returns True."
                    }
                },
                "required": ["message", "module", "error_message", "conversation_mode"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_alarm",
            "description": "Set a timer or alarm with a given time and message. The timezone should be " + TIMEZONE + " tz. If the user dont explicit the time, ask for it. Also, if the the user only give an amount of time, add it to the current time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "trigger_time": {
                        "type": "string",
                        "description": "The time to set the alarm as a timestamp in ISO 8601 format."
                    },                       
                    "message": {
                        "type": "string", 
                        "description": "The message to be said when the alarm or timer is triggered, should have the time when the alarm is set. The language used should be "  + LANGUAGE
                    },
                    "module": {
                        "type": "string", 
                        "enum": ["general"]
                    },
                    "error_message": {
                        "type": "string", 
                        "description": "The message alerting that there has been an issue with the action, the language used should be "  + LANGUAGE
                    }
                },
                "required": ["time", "message", "module", "error_message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "what_time",
            "description": "Returns the current time. The timezone should be " + TIMEZONE + " tz, if the user don't explicit the timezpme.",
                       "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string", 
                        "description": "The current time for the given timezone in the language " + LANGUAGE
                    },
                    "module": {
                        "type": "string", 
                        "enum": ["general"]
                    },
                    "error_message": {
                        "type": "string", 
                        "description": "The message alerting that there has been an issue with the action, the language used should be "  + LANGUAGE
                    }
                },
                "required": ["message", "module", "error_message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_volume",
            "description": "Increase or decrease the volume accordingly to the given value. If the user wants to increase the volume, but don't explicit the value, return 1. If the user wants to decrease the volume, but don't explicit the value, return -1.",
                       "parameters": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "integer", 
                        "description": "The value to increase or decrease the volume."
                    },
                    "module": {
                        "type": "string", 
                        "enum": ["general"]
                    },
                    "error_message": {
                        "type": "string", 
                        "description": "The message alerting that there has been an issue with the action, the language used should be "  + LANGUAGE
                    }
                },
                "required": ["value", "module", "error_message"],
            },
        },
    }       
]