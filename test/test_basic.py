import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

fs = 44100
seconds = 3

print("Recording...")
audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
sd.wait()

write("test.wav", fs, audio)
print("Saved test.wav")
