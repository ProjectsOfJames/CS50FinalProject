# editor.py
def trim_audio(audio, start_sec, end_sec, samplerate):
    start = int(start_sec * samplerate)
    end = int(end_sec * samplerate)
    return audio[start:end]
