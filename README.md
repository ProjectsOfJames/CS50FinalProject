# Obvious Recorder
## Video Demo: <PUT YOUR VIDEO URL HERE-
### Description:

Obvious Recorder is a desktop audio recording application that was built with Python for my CS50 Final Project. The goal of the project was to design and implement a light weight, functional, easy to use recorder. It uses real-world tooling, and event-driven programming concepts such as in the CS50 course. The application allows people to record audio from their microphone, save those recordings to disk and then apply an audio filter in a post-processing manner with the use of FFmpeg, with the use of the simple graphical interface that was built with Tkinter.

The idea behind Obvious Recorder came from an idea before week 9 of CS50 and a personal annoyance with the name of the project being derived from my gamer tag. Audio recording requires interacting with the operating system, external dependencies, asynchronous behavior, and file processing, making it a sufficient test of knowledge and software design, instead of algorithm correctness.

### Application Overview
The application uses a grid layout for logical sections. The top-left area is used for buttons to start and stop a recording. The top-right displays the title of the project. The middle-left section shows the application's status (idle, recording, recording saved). The middle-right section contains the drop down that allows a user to select an audio filter if they wanted to. The lastly at the bottom there is a quit button to safely exit the app.

### Flow of the app:
- User clicks Start to begin recording audio
    - While recording, other controls are disabled to prevent invalid states
- Clicking Stop ends the recording and saves it to disk under recordings folder
- User can optionally apply an Echo filter to the recorded audio
- Application converts recordings to MP3 format using FFmpeg

### File Structure and Responsibilities
The project is split across multiple folders and Python files to maintain clarity and separation of concerns.

**main.py**
File responsible for the GUI, it creates the Tkinter window, defines the layout with frames and grid configuration, and links UI elements (like the buttons and dropdowns) to handler functions. Keeps the GUI code isolated and with a sole focus on the look and interaction of the app.

**recorder.py**
Contains the AudioRecorder class, which manages audio capture. This makes use of third-party libraries to access the microphone, record the raw audio data, and then write the recording to a WAV file. Also provides functionality to convert WAV recordings into MP3 format with the use of FFmpeg. With isolating recording logic here, the application becomes easier to test and extend.

**filters.py**
File contains audio post-processing logic. Currently due to time constraints, it only implements an Echo filter using the FFmpeg command-line arguments. The filter is then applied after recording instead of during, simplifying synchronization. More filters can be added and placeholder reverb exists, but was left unimplemented due to time constraints.

**utils.py**
Module that acts as a control layer between the GUI and core logic. This contains the button and dropdown handlers (start and stop recordings, applying filters, and safely exiting the program). It also includes a helper function to verify that FFmpeg is installed and accessible through the system PATH. Moving these handlers out of main.py helped reduce coupling and improved maintainability.

### Design Choices
- Tkinter was chosen for the GUI due to the ease of adding it due to being included with Python
- FFmpeg was used for audio conversion and filtering instead of trying to 'reinvent the wheel' since FFmpeg is an industry-standard tool
- Filters are applied after recording instead of during. 
- The project is structured to avoid circular dependencies and tightly coupled code. The GUI does not directly manipulate audio files, and the audio logic does not depend on Tkinter. 

### Limitations and Future Improvements
    #All currently know limitations are due to time constraints

- Want to add additional filters
- Allow the user to , display recording duration in real time, or allow the user to select an input device.
- Avoid making duplicate recording files by allowing user to choose output formats before recording (now each recording has a .wav and .mp3 file, and each filter makes 2 more files in each format)
- Display recording duration
- Select input device to record
