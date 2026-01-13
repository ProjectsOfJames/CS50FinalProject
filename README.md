# Obvious Recorder
## Video Demo: https://www.youtube.com/watch?v=3r4b-J2Q9sA
### Description:

Obvious Recorder is a desktop audio recording application that was built with Python for my CS50 Final Project. The goal of the project was to design and implement a light weight, functional, easy to use recorder. It uses real-world tooling, and event-driven programming concepts such as in the CS50 course. The application allows people to record audio from their microphone, save those recordings to disk and then apply an audio filter in a post-processing manner with the use of FFmpeg, with the use of the simple graphical interface that was built with Tkinter.

The idea behind Obvious Recorder came from an idea before week 9 of CS50 and a personal annoyance, with the name of the project being derived from my gamer tag. Audio recording requires interacting with the operating system, external dependencies, asynchronous behavior and file processing, making it a sufficient test of knowledge and software design, instead of algorithm correctness.

### Application Overview
The application uses a grid layout for logical sections. The top-left area is used for buttons to start and stop a recording. The top-right displays the title of the project. The middle-left section shows the application's status (idle, recording, recording saved). The middle-right section contains the drop down that allows a user to select an audio filter if they wanted to. The lastly at the bottom there is a quit button to safely exit the app.

### Usage of the app:
- User clicks Start to begin the mic recording
    - While recording, other controls are disabled to prevent possible issues
- Clicking Stop ends the recording and saves it under recordings folder
- User can use the drop down to apply an Echo filter to the recorded audio
- Application automatically converts recordings to MP3 using FFmpeg

### File Structure and Responsibilities
The project is split across multiple folders and Python files to maintain clear separation of logic. Folder struction consists of main project folder that has a src sub-folder, recording sub-folders, requirements.txt and README.md , Then src folder contains all python files and rocording folder is where all recording are saved

**main.py**
File responsible for the GUI, it creates the Tkinter window, defines the layout with frames and grid configuration, and links UI elements (like the buttons and dropdowns) to handler functions. Keeps the GUI code isolated and with a sole focus on the look and interaction of the app.

**recorder.py**
Contains the AudioRecorder class, which manages the audio capturing. This makes use of third-party libraries to access the microphone, record the raw audio data, and then write the recording to a WAV file. Also provides functionality to convert WAV recordings into MP3 format with the use of FFmpeg. Due to isolating recording logic here, application becomes easier to test and expand.

**filters.py**
File contains audio filter logic. Currently due to time constraints, it only implements an Echo filter using the FFmpeg command-line arguments. The filter is then applied after recording instead of during, simplifying synchronization. More filters can be added and placeholder reverb exists, but was left unimplemented due to time constraints.

**utils.py**
Module that acts as the control layer between the GUI and core logic. This contains the button and dropdown handlers (such as start and stop recording, applying filters and quiting the program). Also includes a helper function to verify that FFmpeg is installed and accessible through the system PATH. Moved these handlers out of main.py to help abstract logic and improved maintainability.

### Design Choices
- Tkinter was used for the GUI since it is included with Python
- FFmpeg was used for audio conversion and filtering instead of trying to 'reinvent the wheel', since FFmpeg is a well known industry-standard tool
- Filters are applied after recording instead of during
- The GUI does not directly manipulate audio files, and the audio logic does not depend on Tkinter

### Limitations and Future Improvements
    #All currently know limitations are due to time constraints

- Want to add additional filters
- Better trim functionality with a visual display of start and end

### Curent Planning
- Currently no future planning
