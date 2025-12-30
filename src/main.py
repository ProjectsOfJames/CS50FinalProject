import tkinter as tk
from tkinter import messagebox
from recorder import AudioRecorder
from filters import apply_echo

class RecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Obvious Recorder")
        self.root.geometry("600x300")
        self.root.minsize(500, 280)

        self.recorder = AudioRecorder()
        self.recording_path = None

        self._build_ui()

    # set up UI
    ###########################
    def _build_ui(self):
        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)

        # Top Left
        ###########################
        control_frame = tk.Frame(self.root, bd=2, relief="solid")
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Start
        self.start_button = tk.Button(
            control_frame,
            text="Start",
            height=2,
            command=self.start_recording
        )
        self.start_button.pack(fill="x", padx=5, pady=(10, 5))

        # Stop
        self.stop_button = tk.Button(
            control_frame,
            text="Stop",
            height=2,
            state=tk.DISABLED,
            command=self.stop_recording
        )
        self.stop_button.pack(fill="x", padx=5, pady=(0, 10))

        # Top Right
        ###########################
        title_frame = tk.Frame(self.root, bd=2, relief="solid")
        title_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Project Name
        title_label = tk.Label(
            title_frame,
            text="Obvious Recorder",
            font=("Arial", 20, "bold")
        )
        title_label.pack(expand=True)

        # Middle Left
        ###########################
        status_frame = tk.Frame(self.root, bd=2, relief="solid")
        status_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Status
        self.status_label = tk.Label(
            status_frame,
            text="Status: Idle",
            anchor="w"
        )
        self.status_label.pack(fill="both", padx=10, pady=10)

        # Middle Right
        ###########################
        filter_frame = tk.Frame(self.root, bd=2, relief="solid")
        filter_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # Filter
        filter_label = tk.Label(filter_frame, text="Apply Filter:")
        filter_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.filter_var = tk.StringVar(value="None")
        self.filter_var.trace_add("write", self.on_filter_selected)

        self.filter_dropdown = tk.OptionMenu(
            filter_frame,
            self.filter_var,
            "None",
            "Echo"
        )
        self.filter_dropdown.pack(fill="x", padx=10, pady=(0, 10))

        # Bottom
        ###########################

        # Quit
        quit_button = tk.Button(
            self.root,
            text="Quit",
            height=2,
            command=self.root.quit
        )
        quit_button.grid(
            row=2,
            column=0,
            columnspan=2,
            padx=10,
            pady=10,
            sticky="nsew"
        )

    
    # Button handlers
    ###########################
    def start_recording(self):
        try:
            self.recorder.start()
            self.status_label.config(text="Status: Recording...", fg="red")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.filter_dropdown.config(state=tk.DISABLED) 
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def stop_recording(self):
        try:
            wav_path = self.recorder.stop()
            mp3_path = self.recorder.convert_to_mp3(wav_path)
            self.filter_dropdown.config(state=tk.NORMAL)
            
            self.last_wav = wav_path

            self.status_label.config(
                text="Status: Saved recording",
                fg="green"
            )

            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

            messagebox.showinfo(
                "Recording Saved",
                f"Saved as:\n{mp3_path}"
            )

        except Exception as e:
            messagebox.showerror("Error", str(e))
        
    def apply_echo_filter(self):
        try:
            output = self.last_wav.replace(".wav", "_echo.wav")
            apply_echo(self.last_wav, output)
            self.recorder.convert_to_mp3(output)

            messagebox.showinfo(
                "Echo Applied",
                "Echo effect applied successfully."
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # reverb to do in future (time constraints)
    '''
    def apply_reverb_filter(self):
    '''
    def on_filter_selected(self, *_):
        selected = self.filter_var.get()

        if selected == "Echo":
            self.apply_echo_filter()
        else:
            self.remove_filters()



def main():
    root = tk.Tk()
    app = RecorderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
