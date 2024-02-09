import subprocess
import re
from debug import *
from settings import VOLUME_LEVELS
import alsaaudio


pattern = re.compile(r'(\S[^:]*):\s*(.*)')
parsed_data = {}
VOLUME_STATUS = "original"

def get_volume():
    try:
        # Run amixer command and get output
        result = subprocess.run(['amixer', 'get', 'Master'], stdout=subprocess.PIPE)

        # Decode the result and parse volume
        output = result.stdout.decode('utf-8')

        # Regular expression to extract volume percentage
        # This might vary depending on your amixer version and output format
        match = re.search(r'\[([0-9]+)%\]', output)
        if match:
            return int(match.group(1))
        else:
            return None
    except Exception as e:
        error_handler(e)

volume = get_volume()



def get_sink_inputs():
    try:
        result = subprocess.run(["pactl", "list", "sink-inputs"], stdout=subprocess.PIPE)
        output = result.stdout.decode()
        print_me(output)
        current_key = None

        sink_input_sections = re.split(r'(Sink Input #\d+)', output)[1:]
        sink_inputs = []
        j = 0
        for i in range(0, len(sink_input_sections), 2):
            section_title = sink_input_sections[i].strip("Sink Input #")
            section_data = sink_input_sections[i + 1]

            # Parse the data
            parsed_data = {'sink_id': section_title}
            current_key = None

            for line in section_data.split('\n'):
                if line.strip():
                    match = pattern.match(line.strip())
                    if match:
                        current_key, value = match.groups()
                        parsed_data[current_key] = value
                    elif current_key:  # Handle multiline values
                        parsed_data[current_key] += ' ' + line.strip()

            sink_inputs.append(parsed_data)            
            volume = sink_inputs[j]["Volume"].split("/")
            sink_inputs[j]["Volume"] = ((volume[0].strip()).split(":"))[1]
            j += 1

        
        # Extract sink input IDs
        return sink_inputs
    except Exception as e:
        error_handler(e)
        

# Decrease volume of all sink inputs
def decrease_volume(volume_percent):
    try:
        for sink_input in get_sink_inputs():
            print_me(f"Volume to decrease: {sink_input['Volume']}")  

            volume = int((volume_percent * int(sink_input["Volume"])) / 100)  # PulseAudio volume format
            print_me(f"Volume decrease: {volume}")  
            subprocess.run(["pactl", "set-sink-input-volume", sink_input["sink_id"], str(volume)])
            return "volume_decreased"
    except Exception as e:
        error_handler(e)

# Decrease volume of all sink inputs
def original_volume(volume_percent):
    try:
        for sink_input in get_sink_inputs():
            print_me(f"Volume original: {sink_input['Volume']}")
            volume = int(int(sink_input["Volume"]) / (volume_percent/100))  # PulseAudio volume format
            if volume > 65536:
                volume = 65536
            print_me(f"Volume original: {volume}, sink_id: {sink_input['sink_id']}")  

            subprocess.run(["pactl", "set-sink-input-volume", sink_input["sink_id"], str(volume)])
            return "original"
    except Exception as e:
        error_handler(e)

def set_volume(volume_level):
    try:
        # volume_level should be between 0 and 100
        true_levels = 100/VOLUME_LEVELS
        volume_level = volume_level*true_levels
        mixer = alsaaudio.Mixer()  
        mixer.setvolume(volume_level)
    except Exception as e:
        error_handler(e)
