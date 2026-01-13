# plotter.py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AudioPlotter:
    # Smooth scrolling waveform plot for Tkinter.
    
    def __init__(self, parent, samplerate, buffer_seconds=5):
        self.samplerate = samplerate
        self.buffer_seconds = buffer_seconds
        self.buffer_size = int(samplerate * buffer_seconds)
        self.buffer = np.zeros(self.buffer_size)

        # Create matplotlib Figure
        self.fig, self.ax = plt.subplots(figsize=(6, 2))
        self.line, = self.ax.plot(self.buffer)
        self.ax.set_ylim(-1, 1)
        self.ax.set_xlim(0, self.buffer_size)
        self.ax.set_title("Audio Waveform")
        self.ax.set_xlabel("Samples")
        self.ax.set_ylabel("Amplitude")
        self.ax.grid(True)

        # Embed in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def update(self, new_chunk):
        # Append new_chunk to rolling buffer and update plot
        
        if len(new_chunk.shape) > 1:
            new_chunk = new_chunk[:, 0]  # take first channel if stereo

        # If chunk longer than buffer, take last samples
        if len(new_chunk) > self.buffer_size:
            new_chunk = new_chunk[-self.buffer_size:]

        # Shift buffer left and append new_chunk at the end
        shift_len = len(new_chunk)
        self.buffer = np.roll(self.buffer, -shift_len)
        self.buffer[-shift_len:] = new_chunk

        # Update line data
        self.line.set_ydata(self.buffer)
        self.canvas.draw()

    def plot_full_audio(self, audio):
        # Display a full static waveform (used after record/import)
        if audio.ndim > 1:
            audio = audio[:, 0]

        self.ax.clear()
        self.ax.plot(audio, linewidth=0.5)
        self.ax.set_ylim(-1, 1)
        self.ax.set_title("Audio Waveform")
        self.ax.set_xlabel("Samples")
        self.ax.set_ylabel("Amplitude")
        self.ax.grid(True)

        self.canvas.draw()

