import time
from recorder import AudioRecorder

rec = AudioRecorder()

print("Recording...")
rec.start()
time.sleep(5)
wav_file = rec.stop()

print("Saved:", wav_file)

mp3_file = rec.convert_to_mp3(wav_file)
print("Converted:", mp3_file)
