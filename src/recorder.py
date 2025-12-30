import sounddevice as sd
import numpy as np
import wave
import subprocess
import threading
import os
from datetime import datetime


class AudioRecorder:
    def __init__(self, samplerate=44100, channels=1):
        self.samplerate = samplerate
        self.channels = channels
        self.recording = False
        self.audio_data = []
        self.stream = None

    # Internal callback
    ###########################
    def _callback(self, indata, frames, time, status):
        if status:
            print(status)
        if self.recording:
            self.audio_data.append(indata.copy())

    # Start recording
    ###########################
    def start(self):
        if self.recording:
            raise RuntimeError("Recording already in progress")

        self.audio_data = []
        self.recording = True

        self.stream = sd.InputStream(
            samplerate= self.samplerate,
            channels= self.channels,
            callback= self._callback
        )
        self.stream.start()

    # Stop recording & save WAV
    ###########################
    def stop(self, output_dir="recordings"):
        if not self.recording:
            raise RuntimeError("No active recording to stop")

        self.recording = False
        self.stream.stop()
        self.stream.close()

        os.makedirs(output_dir, exist_ok=True)

        filename = self._generate_filename("wav")
        filepath = os.path.join(output_dir, filename)

        audio = np.concatenate(self.audio_data, axis=0)
        self._save_wav(filepath, audio)

        return filepath


    # WAV saving
    ###########################
    def _save_wav(self, filepath, audio):
        audio_int16 = np.int16(audio * 32767)

        with wave.open(filepath, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(self.samplerate)
            wf.writeframes(audio_int16.tobytes())

    
    # Convert WAV to MP3
    ###########################
    def convert_to_mp3(self, wav_path, delete_wav=False):
        mp3_path = wav_path.replace(".wav", ".mp3")

        command = [
            "ffmpeg",
            "-y",
            "-i", wav_path,
            mp3_path
        ]

        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if delete_wav:
            os.remove(wav_path)

        return mp3_path

    # Filename helper
    ###########################
    def _generate_filename(self, ext):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"recording_{timestamp}.{ext}"
