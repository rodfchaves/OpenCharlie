"""
Checks if the wake word is present. If true, it will call the main_prompt function. Returns False if the wake word is not present.

"""
import numpy as np
import torch
import torch.nn as nn
from debug import *
import speechpy
from settings import *
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
        x = torch.flatten(x, 1)
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

model = AudioClassifier()
model.load_state_dict(torch.load(model_path))
model.eval()
input_size = 422

def preprocess_mfcc(mfcc):
    mfcc = np.transpose(mfcc) #we need to transpose the mfccs because we used librosa to generate the model and speechfy to generate the mfccs here
    padding_length = input_size - mfcc.shape[1]
    if padding_length > 0:
        mfcc = np.pad(mfcc, ((0, 0), (0, padding_length)), mode='constant', constant_values=0)
    elif padding_length < 0:
        mfcc = mfcc[:, :input_size]
    
    mfcc_tensor = torch.tensor(mfcc, dtype=torch.float32,   device=torch.device("cpu"))
    tensor_cpu = mfcc_tensor.cpu()
    mfcc_stacked = torch.stack([tensor_cpu, tensor_cpu], dim=0) 

    return mfcc_stacked

def is_wake(frames):
    global CONVERSATION_MODE
    segment_frames = (1 * (RATE / CHUNK))

    segments = []
    i = 0
    number_segments = math.ceil(len(frames) / segment_frames)
    for segment in range(number_segments):
        segments.append(frames[i:i+int(segment_frames)])
        i += int(segment_frames)

    for idx, segment in enumerate(segments):    
        try:
            frames_bytes = (b''.join(segment))
            audio_int16 = np.frombuffer(frames_bytes, dtype=np.int16)
            audio_float32 = audio_int16.astype(np.float32) / 32768.0 #normalize to match librosa's output

            mfccs = speechpy.feature.mfcc(audio_float32, sampling_frequency=RATE, frame_length=0.025, frame_stride=0.01, num_filters=40, fft_length=2048, num_cepstral=30)       
            features = preprocess_mfcc(mfccs)
            with torch.no_grad():
                result = softmax(model(features))[0][0]
                print(f"Wake word result: {result}")
                if result < 0.1:
                    return True
    
        except Exception as e:
            print(e)
            error_handler(e)
    
    return False
