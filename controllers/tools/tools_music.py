from settings import LANGUAGE

"""
This file contains the tools that are used by the main controller when it comes to music.
Tools:
    play_music
    pause_playback
    resume_playback
    seek_to_position
    skip_to_next
    skip_to_previous
    toggle_shuffle
    get_information
    change_device
"""

tools_music = [
    {
        "type": "function",
        "function": {
            "name": "play_music",
            "description": "Search for a song, artist, podcast, show, audiobook, episode, playlist or album on a music player and play it. This is not for pause or resume, but just to play a new song.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The name of the song, artist, podcast, show, audiobook, episode, playlist or album, e.g. The Beatles."
                    },
                    "track_type": {
                        "type": "string", 
                        "enum": ["track", "artist", "album", "playlist", "show", "episode", "audiobook"],
                        "description": "The type of the element, e.g. album. Should default to track if you are not sure."
                    },
                    "message": {
                        "type": "string", 
                        "description": "The message alerting which music is playing."
                    },
                    "error_message": {
                        "type": "string", 
                        "description": "The message alerting that there has been an issue with the action, the language used should be "  + LANGUAGE
                    },
                    "module": {
                        "type": "string", 
                        "enum": ["music_module"]
                    }
                },
                "required": ["query", "track_type", "message", "module", "error_message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "pause_playback",
            "description": "If there is a pause or stop command to pause the music or playback, pause everything.",
            "parameters": {
                "type": "object",
                "properties": {                    
                    "module": {
                        "type": "string", 
                        "enum": ["music_module"]
                    },
                    "error_message": {
                        "type": "string", 
                        "description": "The message alerting that there has been an issue with the action, the language used should be "  + LANGUAGE
                    }
                },
                "required": ["module", "error_message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "resume_playback",
            "description": "If there is a resume command, resume everything. ",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {
                        "type": "string", 
                        "enum": ["music_module"]
                    },
                    "error_message": {
                        "type": "string", 
                        "description": "The message alerting that there has been an issue with the action, the language used should be "  + LANGUAGE
                    }
                },
                "required": ["music_module", "error_message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "seek_to_position",
            "description": "If there is a seek command, seek to a given position. ",
            "parameters": {
                "type": "object",
                "properties": {
                    "position_ms": {
                        "type": "integer",
                        "description": "The position in milliseconds to seek to, it can be negative if the user wants to go back."
                    },
                    "module": {
                        "type": "string", 
                        "enum": ["music_module"]
                    },
                    "error_message": {
                        "type": "string", 
                        "description": "The message alerting that there has been an issue with the action, the language used should be "  + LANGUAGE
                    }
                },
                "required": ["position_ms", "module", "error_message"]
            }           
        }
    },
    {
        "type": "function",
        "function": {
            "name": "skip_to_next",
            "description": "If there is a skip to next command, skip to the next song. ",
            "parameters": {
                "type": "object",
                "properties": {
                    "jumps": {
                        "type": "integer",
                        "description": "The number of songs to jump, if the user wants to jump 2 songs, it should be 2. If no value was given by the user, should return 1."
                    },
                    "module": {
                        "type": "string", 
                        "enum": ["music_module"]
                    },
                    "error_message": {
                        "type": "string", 
                       "description": "The message alerting that there has been an issue with the action, the language used should be "  + LANGUAGE
                    }
                },
                "required": ["jumps", "module", "error_message"]
            }           
        }
    },
    {
        "type": "function",
        "function": {
            "name": "skip_to_previous",
            "description": "If there is a skip to next command, skip to the next song. ",
            "parameters": {
                "type": "object",
                "properties": {
                    "jumps": {
                        "type": "integer",
                        "description": "The number of songs to jump BACK, if the user wants to jump 2 songs, it should be 2. If no value was given by the user, should return 1."
                    },
                    "module": {
                        "type": "string", 
                        "enum": ["music_module"]
                    },
                    "error_message": {
                        "type": "string", 
                       "description": "The message alerting that there has been an issue with the action, the language used should be "  + LANGUAGE
                    }                    
                },
                "required": ["jumps", "module", "error_message"]
            }           
        }
    },
    {
        "type": "function",
        "function": {
            "name": "toggle_shuffle",
            "description": "If there is a toggle shuffle command, toggle shuffle. ",
            "parameters": {
                "type": "object",
                "properties": {                    
                    "module": {
                        "type": "string", 
                        "enum": ["music_module"]
                    },
                    "error_message": {
                        "type": "string", 
                        "description": "The message alerting that there has been an issue with the action."
                    }                    
                },
                "required": ["module", "error_message"]
            }                      
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_information",
            "description": "If the user wants information about the current song, artist, album, playlist, show, episode or audiobook",
            "parameters": {
                "type": "object",
                "properties": {                    
                    "module": {
                        "type": "string", 
                        "enum": ["music_module"]
                    },
                    "error_message": {
                        "type": "string", 
                        "description": "The message alerting that there has been an issue with the action, the language used should be "  + LANGUAGE
                    }                    
                },
                "required": ["module", "error_message"]
            }
        
        }
    },
    {
        "type": "function",
        "function": {
            "name": "change_device",
            "description": "If the user wants to change devices to play the music, change to the next device.",
            "parameters": {
                "type": "object",
                "properties": {                    
                    "module": {
                        "type": "string", 
                        "enum": ["music_module"]
                    },
                    "error_message": {
                        "type": "string", 
                        "description": "The message alerting that there has been an issue with the action, the language used should be "  + LANGUAGE
                    }                    
                },
                "required": ["module", "error_message"]
            }
        
        }
    }
]