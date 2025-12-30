import numpy as np
import wave


def load_wav(filepath):
    with wave.open(filepath, "rb") as wf:
        params = wf.getparams()
        frames = wf.readframes(wf.getnframes())
        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
        audio /= 32767.0
    return audio, params


def save_wav(filepath, audio, params):
    audio = np.clip(audio, -1.0, 1.0)
    audio_int16 = (audio * 32767).astype(np.int16)

    with wave.open(filepath, "wb") as wf:
        wf.setparams(params)
        wf.writeframes(audio_int16.tobytes())


# Echo Filter
###########################
def apply_echo(
    input_path,
    output_path,
    delay_ms=400,
    decay=0.5
):
    audio, params = load_wav(input_path)
    framerate = params.framerate

    delay_samples = int(framerate * delay_ms / 1000)

    echo_audio = np.zeros(len(audio) + delay_samples)
    echo_audio[:len(audio)] += audio
    echo_audio[delay_samples:] += audio * decay

    save_wav(output_path, echo_audio, params)


# Reverb Filter (for future)
###########################
