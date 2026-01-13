# main.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import numpy as np
import sounddevice as sd
import subprocess
import os

from recorder import AudioRecorder
from filters import apply_echo
from utils import list_input_devices, select_audio_file
from editor import trim_audio
from plotter import AudioPlotter


class RecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Obvious Recorder")
        self.root.geometry("900x500")
        self.root.minsize(800, 450)

        # Core
        self.recorder = AudioRecorder()
        self.audio_buffer = None
        self.original_buffer = None
        self.play_thread = None

        # GUI variables
        self.selected_device = tk.StringVar()
        self.codec_var = tk.StringVar(value="wav")
        self.start_trim = tk.DoubleVar(value=0)
        self.end_trim = tk.DoubleVar(value=1)
        self.filter_var = tk.StringVar(value="None")

        # Build UI
        self._build_ui()

        # Start waveform update loop
        self.root.after(50, self.update_plot)

    ###########################
    # UI BUILD
    ###########################
    def _build_ui(self):
        # Top frame: device + codec + buttons
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(top_frame, text="Input Device:").pack(side="left")
        devices = list_input_devices(windows_only=True)
        self.selected_device.set(devices[0] if devices else "")
        self.device_dropdown = ttk.OptionMenu(

            top_frame, self.selected_device, self.selected_device.get(), *devices
        )
        self.device_dropdown.pack(side="left", padx=5)

        tk.Label(top_frame, text="Save Codec:").pack(side="left", padx=(20, 0))
        codec_menu = ttk.OptionMenu(top_frame, self.codec_var, "wav", "wav", "mp3")
        codec_menu.pack(side="left", padx=5)

        self.start_button = tk.Button(top_frame, text="Start", command=self.start_recording)
        self.start_button.pack(side="left", padx=5)
        self.stop_button = tk.Button(top_frame, text="Stop", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(side="left", padx=5)
        self.play_button = tk.Button(top_frame, text="Play Trimmed", command=self.play_audio, state=tk.DISABLED)
        self.play_button.pack(side="left", padx=5)
        self.stop_play_button = tk.Button(top_frame, text="Stop Playback", command=self.stop_audio, state=tk.DISABLED)
        self.stop_play_button.pack(side="left", padx=5)
        self.save_button = tk.Button(top_frame, text="Save File", command=self.save_file, state=tk.DISABLED)
        self.save_button.pack(side="left", padx=5)
        self.import_button = tk.Button(top_frame, text="Import File", command=self.import_file)
        self.import_button.pack(side="left", padx=5)

        # Middle frame: left = status/filter, right = waveform + trimming
        middle_frame = tk.Frame(self.root)
        middle_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Left: Status + filter
        left_frame = tk.Frame(middle_frame, bd=2, relief="solid")
        left_frame.pack(side="left", fill="y", padx=5, pady=5)

        self.status_label = tk.Label(left_frame, text="Status: Idle", anchor="w")
        self.status_label.pack(fill="x", padx=10, pady=10)

        tk.Label(left_frame, text="Apply Filter:").pack(anchor="w", padx=10)
        self.filter_var.trace_add("write", lambda *_: self.apply_filter())
        self.filter_dropdown = ttk.OptionMenu(left_frame, self.filter_var, "None", "None", "Echo")
        self.filter_dropdown.pack(fill="x", padx=10, pady=5)

        # Right: waveform + trimming
        right_frame = tk.Frame(middle_frame, bd=2, relief="solid")
        right_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.plotter = AudioPlotter(right_frame, self.recorder.samplerate, buffer_seconds=5)

        tk.Label(right_frame, text="Trim Audio (seconds)").pack(pady=5)
        self.start_slider = tk.Scale(right_frame, variable=self.start_trim, from_=0, to=1,
                                     orient="horizontal", resolution=0.01, label="Start")
        self.start_slider.pack(fill="x", padx=10, pady=5)
        self.end_slider = tk.Scale(right_frame, variable=self.end_trim, from_=0, to=1,
                                   orient="horizontal", resolution=0.01, label="End")
        self.end_slider.pack(fill="x", padx=10, pady=5)

        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill="x", padx=10, pady=5)
        self.info_label = tk.Label(bottom_frame, text="Ready", anchor="w")
        self.info_label.pack(fill="x")

    ###########################
    # RECORDING
    ###########################
    def start_recording(self):
        if not self.selected_device.get():
            messagebox.showerror("Error", "No input device selected.")
            return
        # Check if desktop audio
        is_loopback = "Desktop Audio" in self.selected_device.get()
        device_index = int(self.selected_device.get().split(":")[0])
        self.recorder.set_device(device_index, loopback=is_loopback)

        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.status_label.config(text="Recording...", fg="blue")
        self.audio_buffer = None

        threading.Thread(target=self.recorder.start, daemon=True).start()

    def stop_recording(self):
        audio = self.recorder.stop()

        if audio is None:
            self.status_label.config(text="Status: No audio captured", fg="red")
            return

        # Store audio
        self.audio_buffer = audio
        self.original_buffer = audio.copy()

        # Duration in seconds
        duration = len(audio) / self.recorder.samplerate

        # Update trim sliders
        self.start_slider.config(from_=0, to=duration)
        self.end_slider.config(from_=0, to=duration)
        self.start_slider.set(0)
        self.end_slider.set(duration)

        # Update waveform
        self.plotter.plot_full_audio(audio)

        # UI state
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.play_button.config(state="normal")
        self.save_button.config(state="normal")

        self.status_label.config(
            text=f"Recording stopped ({duration:.2f}s)",
            fg="green"
        )


    ###########################
    # PLOT UPDATE
    ###########################
    def update_plot(self):
        if self.recorder.recording:
            chunk = self.recorder.get_live_chunk()
            if chunk is not None:
                self.plotter.update(chunk)

        self.root.after(30, self.update_plot)

    ###########################
    # PLAYBACK
    ###########################
    def play_audio(self):
        if self.audio_buffer is None:
            return
        start_sec = self.start_trim.get()
        end_sec = self.end_trim.get()
        trimmed = trim_audio(self.audio_buffer, start_sec, end_sec, self.recorder.samplerate)

        if self.play_thread is not None and self.play_thread.is_alive():
            sd.stop()
        self.stop_play_button.config(state="normal")
        self.play_thread = threading.Thread(target=lambda: sd.play(trimmed, self.recorder.samplerate), daemon=True)
        self.play_thread.start()

    def stop_audio(self):
        sd.stop()
        self.stop_play_button.config(state="disabled")

    ###########################
    # FILE HANDLERS
    ###########################
    def save_file(self):
        if self.audio_buffer is None:
            messagebox.showwarning("No audio", "Record or import audio first.")
            return

        start_sec = self.start_trim.get()
        end_sec = self.end_trim.get()
        trimmed = trim_audio(
            self.audio_buffer,
            start_sec,
            end_sec,
            self.recorder.samplerate
        )

        codec = self.codec_var.get()
        path = filedialog.asksaveasfilename(
            defaultextension=f".{codec}",
            filetypes=[("Audio Files", "*.wav *.mp3")]
        )
        if not path:
            return

        # Save using recorder
        saved_path = self.recorder.save(trimmed, codec=codec)

        # Move to user-selected path
        os.replace(saved_path, path)

        messagebox.showinfo("Saved", f"File saved as {path}")
        self.info_label.config(text=f"Saved: {path}")


    def import_file(self):
        path = select_audio_file()
        if not path:
            return

        # Convert MP3 → WAV if needed
        if path.lower().endswith(".mp3"):
            temp_wav = "temp_import.wav"
            subprocess.run(
                ["ffmpeg", "-y", "-i", path, temp_wav],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            path = temp_wav

        # Load WAV manually
        import soundfile as sf
        audio, sr = sf.read(path, dtype="float32")

        if sr != self.recorder.samplerate:
            messagebox.showerror(
                "Sample Rate Mismatch",
                f"Expected {self.recorder.samplerate} Hz, got {sr} Hz"
            )
            return

        if audio.ndim > 1:
            audio = audio[:, 0]

        self.audio_buffer = audio
        self.original_buffer = audio.copy()

        duration = len(audio) / self.recorder.samplerate
        self.start_slider.config(to=duration)
        self.end_slider.config(to=duration)
        self.start_slider.set(0)
        self.end_slider.set(duration)

        self.status_label.config(
            text=f"Imported file. Duration: {duration:.2f}s",
            fg="green"
        )

        self.play_button.config(state="normal")
        self.save_button.config(state="normal")


    ###########################
    # FILTER
    ###########################
    def apply_filter(self):
        if self.audio_buffer is None:
            return

        selected = self.filter_var.get()

        if selected == "Echo":
            temp_in = "temp_filter_in.wav"
            temp_out = "temp_filter_out.wav"

            # Write current audio to temp WAV
            self.recorder._save_wav(temp_in, self.audio_buffer)

            # Apply echo filter
            apply_echo(temp_in, temp_out)

            # Reload filtered audio
            import soundfile as sf
            audio, sr = sf.read(temp_out, dtype="float32")

            if audio.ndim > 1:
                audio = audio[:, 0]

            self.audio_buffer = audio

            # Cleanup
            os.remove(temp_in)
            os.remove(temp_out)

            self.status_label.config(text="Filter applied: Echo", fg="green")

        elif selected == "None":
            if self.original_buffer is not None:
                self.audio_buffer = self.original_buffer.copy()
                self.status_label.config(text="Filters cleared", fg="black")



def main():
    root = tk.Tk()
    app = RecorderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
