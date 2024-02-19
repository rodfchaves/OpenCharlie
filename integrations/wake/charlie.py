# Description: Transcribes audio file and checks if the wake word is present. If the wake word is present, it will call the main_prompt function.

import numpy as np
import torch
import torch.nn as nn
from debug import *
import speechpy
from to_write import to_write
from settings import *
from controllers.main import main_prompt
from settings_systems import transcribe_file
from pydub import AudioSegment
from pydub.silence import split_on_silence
from slugify import slugify
import datetime
import math

softmax = torch.nn.Softmax(dim=1)
model_path = 'integrations/wake/charlie_v1_0.pth'

class AudioClassifier(nn.Module):
    def __init__(self):
        super(AudioClassifier, self).__init__()
        self.conv1 = nn.Conv2d(2, 32, kernel_size=5, stride=1, padding=2)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(32, 2, kernel_size=5, stride=1, padding=2)
        self.fc1 = nn.Linear(12660, 64)
        self.fc2 = nn.Linear(64, 2)

    def forward(self, x):
        print(f'x one: {x.shape}')
        x = torch.flatten(x, 1)
        print(f'x two: {x.shape}')
        x = torch.relu(self.fc1(x))
        print(f'x three: {x.shape}')
        x = self.fc2(x)
        print(f'x four: {x.shape}')
        return x

model = AudioClassifier()
model.load_state_dict(torch.load(model_path))
model.eval()
input_size = 422

def preprocess_mfcc(mfcc):
    print(f'mfcc0: ')
    mfcc = np.transpose(mfcc) #we need to transpose the mfccs because we used librosa to generate the model and speechfy to generate the mfccs here
    print(f'mfcc1: ')
    padding_length = input_size - mfcc.shape[1]
    if padding_length > 0:
        mfcc = np.pad(mfcc, ((0, 0), (0, padding_length)), mode='constant', constant_values=0)
    elif padding_length < 0:
        mfcc = mfcc[:, :input_size]
    
    print(f'mfcc2: ')
    mfcc_tensor = torch.tensor(mfcc, dtype=torch.float32,   device=torch.device("cpu"))
    tensor_cpu = mfcc_tensor.cpu()
    mfcc_stacked = torch.stack([tensor_cpu, tensor_cpu], dim=0) 

    # padding_length = 15990 - mfcc.shape[1]
    # if padding_length > 0:
    #     mfcc = np.pad(mfcc, ((0, 0), (0, padding_length)), mode='constant', constant_values=0)
    # elif padding_length < 0:
    #     mfcc = mfcc[:, :15990]
    # print(f'mfcc five: {mfcc.shape}')

    return mfcc_stacked


def buffer_to_segments(audio_buffer, sample_rate=44100, frame_duration=90, padding_duration=300, silence_thresh=-40):
    # Convert the audio buffer to a Pydub AudioSegment
    audio_segment = AudioSegment(
        data=audio_buffer,
        sample_width=2,  # Assuming 16-bit audio
        frame_rate=sample_rate,
        channels=1
    )

    # Split the audio segment on silence (this is a simplistic approach to segmentation)
    segments = split_on_silence(
        audio_segment,
        min_silence_len=frame_duration,  # Minimum length of silence to consider as a split, in milliseconds
        silence_thresh=silence_thresh,   # Silence threshold (dB)
        keep_silence=padding_duration    # Amount of silence to leave at the beginning and end of each segment, in milliseconds
    )

    return segments


def is_wake(frames):
    global CONVERSATION_MODE
    print_me(f'frames(is_wake): {len(frames)}')

    test2_path = 'io/storage/wake-' + slugify(str(datetime.datetime.now().utcnow())) + '.wav'  
    to_write(frames, test2_path)
    segment_frames = (1 * (RATE / CHUNK))

    segments = []
    i = 0
    number_segments = math.ceil(len(frames) / segment_frames)
    print_me(f'segment_frames: {segment_frames}')

    for segment in range(number_segments):
        segments.append(frames[i:i+int(segment_frames)])
        i += int(segment_frames)

    # segments = np.array_split(frames, len(frames) / (1 * (RATE / CHUNK)))

    # segments = buffer_to_segments(frames_bytes, sample_rate=RATE, frame_duration=15, padding_duration=0, silence_thresh=-50)
    print_me(f'Number of segments: {len(segments)}')

    for idx, segment in enumerate(segments):    
        try:
            test_path = 'io/storage/segment-' + slugify(str(datetime.datetime.now().utcnow())) + "-" + str(idx) + '.wav'  
            to_write(segment, test_path)

            frames_bytes = (b''.join(segment))
            audio_int16 = np.frombuffer(frames_bytes, dtype=np.int16)
            audio_float32 = audio_int16.astype(np.float32) / 32768.0 #normalize to match librosa's output

            mfccs = speechpy.feature.mfcc(audio_float32, sampling_frequency=RATE, frame_length=0.025, frame_stride=0.01, num_filters=40, fft_length=2048, num_cepstral=30)       
            print_me("MFCCs generated")
            print_me(f"mfccs.dtype: {mfccs.dtype}")
            features = preprocess_mfcc(mfccs)
            print_me("MFCC processed")
            with torch.no_grad():
                result = softmax(model(features))[0][0]
                print_me(f"Wake word result: {result}")
                if result < 0.1:
                    return True
    
        except Exception as e:
            print(e)
            error_handler(e)
    
    return False
