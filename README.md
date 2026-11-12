# to-do-list

A personal to-do list that lives on your Windows desktop. Tasks are saved locally in a SQLite database, and you can add new ones hands-free by saying **"Hey Jarvis"** followed by your task.

## Features

- **Desktop widget**: a frameless, always-on-the-bottom window that sits in the top-right corner of your screen like a sticky note.
- **Add tasks by typing**: click "Add task..." and type.
- **Add tasks by voice**: say "Hey Jarvis", then speak your task. It is transcribed locally and added to the top of the list.
- **Edit in place**: click a task's text to rewrite it.
- **Check off tasks**: completed tasks get a strikethrough.
- **Delete tasks**: click the `x` on any row.
- **Persistent storage**: everything is saved in a local `tasks.db` file (SQLite), so your list survives restarts.
- **System tray**: closing the window hides it instead of quitting. Use the tray icon to show the window again or quit.

## How voice input works

1. **Wake word**: [openWakeWord](https://github.com/dscripka/openWakeWord) listens for "Hey Jarvis" on your microphone.
2. **Voice activity detection**: once triggered, [Silero VAD](https://github.com/snakers4/silero-vad) records until you stop speaking.
3. **Transcription**: [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (`base` model, CPU, int8) turns the audio into text.
4. **New task**: the text is inserted at the top of your list.

All audio processing happens on your machine.

## Tech stack

- Python 3.9
- [PySide6](https://doc.qt.io/qtforpython-6/) (Qt GUI)
- SQLite (`sqlite3`, built into Python)
- `sounddevice`, `numpy`, `torch`
- `faster-whisper`, `silero-vad`, `openwakeword`

## Project structure

```
to-do-list/
├── main.py        # GUI, database logic, system tray
├── voice.py       # Wake word, VAD, and speech-to-text pipeline
├── tasks.db       # Created automatically on first run
└── assets/
    ├── fonts/     # Roboto and Archivo Black
    └── icons/     # close.png
```

## Getting started

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd to-do-list
```

### 2. Install dependencies

```bash
pip install -r requirements
```

### 3. Run it

```bash
python main.py
```

On first run, the app creates `tasks.db` and adds two starter tasks.

## Configuration

A few values are currently hardcoded. You will likely need to change them for your machine:

| What | Where | Notes |
| --- | --- | --- |
| Wake word model path | `voice.py`, `WakeWordEngine` | Points to the `hey_jarvis_v0.1.onnx` file inside your `openwakeword` install. Update it to match your Python path. |
| Microphone device | `voice.py`, `AudioRecorder.start_recording` | Uses `device=1`. Run `python -c "import sounddevice as sd; print(sd.query_devices())"` to find yours. |
| Window position | `main.py`, `MainWindow.__init__` | Placed assuming a 1920px-wide screen. |
| Wake word sensitivity | `voice.py`, `WakeWordEngine.process_chunk` | Threshold is `0.95`. Lower it if the wake word is not triggering. |
| Whisper model | `voice.py`, `WhisperEngine` | Uses `base`. Try `small` for better accuracy. |

## Future ideas

- Start automatically with Windows
- Move hardcoded paths and device IDs into a config file
- Visual indicator while the app is listening
- Drag to reorder tasks (the database already stores a `position` column)