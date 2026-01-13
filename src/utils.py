# utils.py
import sounddevice as sd
from tkinter import filedialog

def list_input_devices(windows_only=False):
    """
    Returns a list of input devices.
    On Windows, optionally add 'Desktop Audio (loopback)' if WASAPI is available.
    Format: "index: name"
    """
    devices = []
    all_devices = sd.query_devices()
    for idx, dev in enumerate(all_devices):
        if dev['max_input_channels'] > 0:
            devices.append(f"{idx}: {dev['name']}")

    # Add desktop audio option on Windows using WASAPI
    if windows_only:
        for idx, dev in enumerate(all_devices):
            if dev['hostapi'] == sd.query_hostapis().index(next(h for h in sd.query_hostapis() if h['name'] == 'Windows WASAPI')):
                if dev['max_input_channels'] > 0 and "(loopback)" in dev['name']:
                    devices.append(f"{idx}: {dev['name']} (Desktop Audio)")

    return devices

def select_audio_file():
    path = filedialog.askopenfilename(
        filetypes=[("Audio Files", "*.wav *.mp3")]
    )
    return path



def check_ffmpeg():
    # Check whether FFmpeg is installed and available on PATH.
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except FileNotFoundError:
        return False


# Button / UI Handlers
###########################

def handle_start(app):
    # Start audio recording
    if app.recorder.recording:
        return

    app.start_button.config(state="disabled")
    app.stop_button.config(state="normal")
    app.filter_dropdown.config(state="disabled")

    app.recorder.start()
    app.status_label.config(text="Status: Recording...")


def handle_stop(app):
    # Stop audio recording
    if not app.recorder.recording:
        return

    wav_path = app.recorder.stop()
    mp3_path = app.recorder.convert_to_mp3(wav_path)

    app.recording_path = wav_path

    app.status_label.config(text="Status: Saved recording", fg="green")

    app.start_button.config(state="normal")
    app.stop_button.config(state="disabled")
    app.filter_dropdown.config(state="normal")

    from tkinter import messagebox
    messagebox.showinfo(
        "Recording Saved",
        f"Saved as:\n{mp3_path}"
    )


def handle_quit(app):
    # Safely exit the application
    if app.recorder.recording:
        app.recorder.stop()

    app.root.destroy()


def handle_filter_change(app):
    # Apply selected audio filter
    selected = app.filter_var.get()

    if selected == "Echo":
        app.apply_echo_filter()
    else:
        app.remove_filters()
