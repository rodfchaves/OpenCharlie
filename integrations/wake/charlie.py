# Description: Transcribes audio file and checks if the wake word is present. If the wake word is present, it will call the main_prompt function.

import numpy as np
import torch
import torch.nn as nn
from debug import *
import librosa
from audio_input import to_write
from settings import *
from controllers.main import main_prompt

softmax = torch.nn.Softmax(dim=1)
max_length = 613
model_path = 'charlie_v1_0.pth'

class AudioClassifier(nn.Module):
    def __init__(self):
        super(AudioClassifier, self).__init__()
        self.fc1 = nn.Linear(15990, 64)
        self.fc2 = nn.Linear(64, 2)

    def forward(self, x):
        x = torch.flatten(x, 1)
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

model = AudioClassifier()
model.load_state_dict(torch.load(model_path))
model.eval()

def preprocess_audio(mfcc):
    padding_length = max_length - mfcc.shape[1]
    if padding_length > 0:
        mfcc = np.pad(mfcc, ((0, 0), (0, padding_length)), mode='constant', constant_values=0)
    elif padding_length < 0:
        mfcc = mfcc[:, :max_length]
    mfcc_tensor = torch.tensor(mfcc, dtype=torch.float32,   device=torch.device("cpu"))
    tensor_cpu = mfcc_tensor.cpu()
    mfcc_stacked = torch.stack([tensor_cpu, tensor_cpu], dim=0) 
    return mfcc_stacked


def is_wake(frames):
    audio_data = np.frombuffer(frames, dtype=np.int16)
    mfccs = librosa.feature.mfcc(y=audio_data.astype(float), sr=RATE, n_mfcc=30)
    try:
        features = preprocess_audio(mfccs)
        with torch.no_grad():
            result = softmax(model(features))[0][0]
            if result < 0.1 or conversation_mode == True:
                file = to_write(frames)
                transcription = transcribe_file(file)
                conversation_mode = main_prompt(transcription)
                return True
            elif result > 0.9:
                return False
    except Exception as e:
        error_handler(e)

