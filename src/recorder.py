# recorder.py
import sounddevice as sd
import numpy as np
import wave
import subprocess
import os
from datetime import datetime

class AudioRecorder:
    def __init__(self, samplerate=44100, channels=1):
        self.samplerate = samplerate
        self.channels = channels

        self.device_index = None
        self.loopback = False

        self.recording = False
        self.stream = None

        self.audio_chunks = []      # full recording
        self.live_chunk = None      # latest chunk for waveform

    
    # Device selection
    ###########################
    def set_device(self, device_index, loopback=False):
        self.device_index = device_index
        self.loopback = loopback

    
    # Sounddevice callback
    ###########################
    def _callback(self, indata, frames, time, status):
        if status:
            print(status)

        if not self.recording:
            return

        # Copy data to avoid threading issues
        chunk = indata.copy()
        self.audio_chunks.append(chunk)
        self.live_chunk = chunk

    
    # Start recording
    ###########################
    def start(self):
        if self.recording:
            return

        self.audio_chunks = []
        self.live_chunk = None
        self.recording = True

        extra = None
        if self.loopback:
            extra = sd.WasapiSettings(loopback=True)

        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            device=self.device_index,
            channels=self.channels,
            dtype="float32",
            callback=self._callback,
            extra_settings=extra
        )
        self.stream.start()

    
    # Stop recording
    ###########################
    def stop(self):
        if not self.recording:
            return None

        self.recording = False
        self.stream.stop()
        self.stream.close()
        self.stream = None

        if not self.audio_chunks:
            return None

        audio = np.concatenate(self.audio_chunks, axis=0)
        return audio

    
    # Get latest audio chunk (for waveform)
    ###########################
    def get_live_chunk(self):
        return self.live_chunk

    
    # Save audio
    ###########################
    def save(self, audio, codec="wav", output_dir="recordings"):
        os.makedirs(output_dir, exist_ok=True)
        filename = self._generate_filename(codec)
        path = os.path.join(output_dir, filename)

        if codec == "wav":
            self._save_wav(path, audio)
            return path

        if codec == "mp3":
            wav_temp = path.replace(".mp3", ".wav")
            self._save_wav(wav_temp, audio)
            self._convert_to_mp3(wav_temp, path)
            os.remove(wav_temp)
            return path

        raise ValueError("Unsupported codec")

    
    # WAV helper
    ###########################
    def _save_wav(self, filepath, audio):
        audio = np.clip(audio, -1.0, 1.0)
        audio_int16 = (audio * 32767).astype(np.int16)

        with wave.open(filepath, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)
            wf.setframerate(self.samplerate)
            wf.writeframes(audio_int16.tobytes())

    
    # MP3 helper
    ###########################
    def _convert_to_mp3(self, wav_path, mp3_path):
        subprocess.run(
            ["ffmpeg", "-y", "-i", wav_path, mp3_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )


    # Filename helper
    ###########################
    def _generate_filename(self, ext):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"recording_{ts}.{ext}"
