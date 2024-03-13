import json
from audio_output import *
from controllers.alarm import *
from controllers.tools.tools_general import *
from controllers.tools.tools_music import *
from debug import *
from settings_systems import music_module, get_tool_response, voice_me, TIMEZONE

tools = tools + tools_music

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
    if len(transcription) >= 5:
        try:
            query, track_type, function_name, response_message = None, None, None, None
            #get the response from the transcription using tools
            response = get_tool_response(tools, transcription)

            choices = response.get("choices")
            message = choices[0].get("message")
            content = message.get("content")
            tool_calls = message.get("tool_calls")
            if tool_calls: 
                function = tool_calls[0].get("function")
                if function:
                    function_name = function.get("name") or None
                    arguments = json.loads(function.get("arguments")) or None
                    if arguments:
                        #Arguments
                        query = arguments.get("query")
                        track_type = arguments.get("track_type")
                        argument_message = arguments.get("message")
                        track_type = arguments.get("track_type")
                        trigger_time = arguments.get("trigger_time")
                        value = arguments.get("value")
                        module = arguments.get("module")
                        response_message = argument_message
                        jumps = arguments.get("jumps")
                        position_ms = arguments.get("position_ms")
                        error_message = arguments.get("error_message")
                        user_reply = arguments.get("conversation_mode")

                    else:
                        response_message = content

            if function_name == "conversation":
                print("The response message: " + response_message)          
                if user_reply:
                    return voice_me(response_message, True)  
                else:
                    return voice_me(response_message, False)

            if response_message:
                print("The response message: " + response_message)
                print("The function name: " + function_name)
                store_conversation_log(response_message, function_name, "gmcharlie")
            
            if module == "music_module":
                if hasattr(music_module, function_name):
                        active_function = getattr(music_module, function_name)                        
                else:
                    print(f"The function {function_name} does not exist in the module.")
                
                if function_name == "play_music":
                    return active_function(query, track_type, response_message)
                elif function_name == "skip_to_next" or "skip_to_previous":
                    return active_function(jumps)
                elif function_name == "seek_to_position":
                    return active_function(position_ms)
                else:
                    return active_function()                  

            if function_name == "set_alarm":
                alarm_thread = SetAlarm(trigger_time, TIMEZONE)            
                alarm = alarm_thread.start()
                if alarm == "alarm_set":
                    return voice_me(response_message)
                elif alarm == "alarm_not_set":
                    return voice_me("Sorry, I couldn't set the alarm. Please try again.")                
        
            if function_name == "set_volume":
                set_volume(value)
            
            return False

        except Exception as e:
            if error_message:
                return voice_me(error_message)
            error_handler(e)
    else:
        return False

