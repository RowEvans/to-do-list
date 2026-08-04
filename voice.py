import sounddevice as sd
import numpy as np
from PySide6.QtCore import QObject, Signal
from faster_whisper import WhisperModel
from silero_vad import load_silero_vad, VADIterator
from openwakeword.model import Model
import torch
import time
import threading

class WakeWordEngine(QObject):
    wake_word_detected = Signal()

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

        self.model = Model(
            wakeword_models=[r"C:\Users\rowan\AppData\Local\Programs\Python\Python39\lib\site-packages\openwakeword\resources\models\hey_jarvis_v0.1.onnx"]
        )

    def process_chunk(self, audio_chunk):
        audio = (audio_chunk.flatten() * 32767).astype(np.int16)

        scores = self.model.predict(audio)

        if scores['hey_jarvis_v0.1'] > 0.95:
            self.callback()
            #self.wake_word_detected.emit()

class AudioRecorder(QObject):

    audio_chunk = Signal(np.ndarray)

    def __init__(self, callback):
        super().__init__()

        self.listeners = []

        self.sample_rate = 16000
        self.channels = 1
        self.stream = None  
        self.callback = callback

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)

        self.callback(indata.copy())

    def start_recording(self):
        try:
            self.stream = sd.InputStream(
                device=1,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="float32",
                blocksize=512,
                callback=self.audio_callback
            )
            self.stream.start()
        except Exception as e:
            print(e)

    def stop_recording(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

class VoiceActivityDetector(QObject):
    def __init__(self, sample_rate):
        super().__init__()

        self.model = load_silero_vad()
        self.sample_rate = sample_rate

        self.iterator = VADIterator(
            self.model,
            sampling_rate=sample_rate
        )

    def is_speech(self, audio_chunk):
        audio_chunk = torch.from_numpy(audio_chunk.flatten())

        event = self.iterator(audio_chunk)

        return event

class WhisperEngine:

    def __init__(self):
        self.model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8"
        )

    def transcribe(self, audio):

        audio = audio.flatten()

        segments, info = self.model.transcribe(
            audio,
            beam_size=5
        )

        return " ".join(segment.text.strip() for segment in segments)

class VoiceManager(QObject):

    task_recognized = Signal(str)

    def __init__(self):
        super().__init__()

        self.recorder = AudioRecorder(self.process_chunk)
        self.whisper = WhisperEngine()
        self.vad = VoiceActivityDetector(self.recorder.sample_rate)
        self.ww = WakeWordEngine(self.start_command)
        #self.ww.wake_word_detected.connect(self.start_command)
        self.silence_chunks = 0
        self.current_audio = []
        self.recording = False

    def listen(self):
        self.recorder.start_recording()

    def start_command(self):
        if self.recording:
            return
        self.recording = True
        self.current_audio = []

    def process_chunk(self, audio_chunk):
        
        if not self.recording:
            self.ww.process_chunk(audio_chunk)

        if not self.recording:
            return

        self.current_audio.append(audio_chunk)

        event = self.vad.is_speech(audio_chunk)
        
        if event is None:
            return
        if 'end' in event:
            self.stop_command()

    def stop_command(self):
        if not self.recording:
            return

        self.recording = False
        if not self.current_audio:
            return 
        audio = np.concatenate(self.current_audio, axis=0)
        threading.Thread(target=self._transcribe, args=(audio,), daemon=True).start()


    def _transcribe(self, audio):
        text = self.whisper.transcribe(audio)
        text = text.strip()
        self.task_recognized.emit(text)

if __name__ == "__main__":
    manager = VoiceManager()
    manager.task_recognized.connect(print)

    manager.listen()

