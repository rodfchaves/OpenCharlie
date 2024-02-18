import json
from audio_output import *
from settings import *
from controllers.alarm import *
from controllers.tools.tools_general import *
from controllers.tools.tools_music import *
from debug import *
from settings_systems import *

tools.append(tools_music[0])

def main_prompt(transcription):
    """
    Controls the main prompt of the voice assistant. It will call the appropriate function based on the transcription.

    Parameters:
    transcription (str): Description of param1.

    Returns:
    type: Description of the return value.

    Raises:
    TBD

    Example:
    main_prompt("Charlie, play the song Hello by Adele")
    Play the song Hello by Adele

    Notes:
    Additional information or context about the function.
    """
    try:

        #get the response from the transcription using tools
        response = get_tool_response(tools, transcription)

        choices = response.get("choices")
        message = choices[0].get("message")
        content = message.get("content")
        tool_calls = message.get("tool_calls")
        function = tool_calls[0].get("function")
        function_name = function.get("name")
        arguments = json.loads(function.get("arguments"))        
        
        #Arguments
        query = arguments.get("query")
        track_type = arguments.get("track_type")
        argument_message = arguments.get("message")
        track_type = arguments.get("track_type")
        trigger_time = arguments.get("trigger_time")
        value = arguments.get("value")

        response_message = argument_message or content      
        if function_name == "conversation":
            print_me("The response message: ", response_message)
            voice_me(response_message)
            return True

        store_conversation_log(response_message, function, "gmcharlie")

        print_me("The query: ", query)
        print_me("The element type: ", track_type)
        print_me("The response message: ", response.content)

        if query and track_type:
            if music_module.play_music(query, track_type, response_message) == False:
                voice_me("Sorry, I couldn't play the music. Please try again.")

        if function_name == "pause":
            music_module.pause_music()

        if function_name == "set_alarm":
            alarm_thread = SetAlarm(trigger_time, TIMEZONE)            
            alarm = alarm_thread.start()
            if alarm == "alarm_set":
                voice_me(response_message)
            elif alarm == "alarm_not_set":
                voice_me("Sorry, I couldn't set the alarm. Please try again.")                
    
        if function_name == "set_volume":
            set_volume(value)
        
        return False

    except Exception as e:
        return error_handler(e)

