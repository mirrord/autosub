
from tempfile import NamedTemporaryFile
import subprocess
import os
from deep_translator import GoogleTranslator
import speech_recognition
from pydub import AudioSegment

class FLACConverter(object): # pylint: disable=too-few-public-methods
    """
    Class for converting a region of an input audio or video file into a FLAC audio file
    """
    def __init__(self, source_path, include_before=0.25, include_after=0.25):
        self.source_path = source_path
        self.include_before = include_before
        self.include_after = include_after

    def __call__(self, region):
        try:
            start, end = region
            start = max(0, start - self.include_before)
            end += self.include_after
            temp = NamedTemporaryFile(suffix='.flac', delete=False)
            command = ["ffmpeg", "-ss", str(start), "-t", str(end - start),
                       "-y", "-i", self.source_path,
                       "-loglevel", "error", temp.name]
            use_shell = True if os.name == "nt" else False
            subprocess.check_output(command, stdin=open(os.devnull), shell=use_shell)
            return temp.read()

        except KeyboardInterrupt:
            return None


class SpeechRecognizer(object): # pylint: disable=too-few-public-methods
    """
    Class for performing speech-to-text for an input FLAC file.
    """
    def __init__(self, rate=44100, retries=3):
        self.rate = rate
        self.retries = retries
        self.recognizer = speech_recognition.Recognizer()

    def __call__(self, data):
        try:
            temp = NamedTemporaryFile(suffix='.flac', delete=False)
            temp.write(data)
            temp.seek(0)
            with speech_recognition.AudioFile(temp.name) as source:
                audio_data = self.recognizer.record(source)
                try:
                    resp = self.recognizer.recognize_google(audio_data)
                except:
                    return ''
                return resp

        except KeyboardInterrupt:
            return None


class Translator(object): # pylint: disable=too-few-public-methods
    """
    Class for translating a sentence from a one language to another.
    """
    def __init__(self, src, dst):
        self.translator = GoogleTranslator(source=src, target=dst)

    def __call__(self, sentence):
        try:
            if not sentence:
                return None
            try:
                return self.translator.translate(sentence)
            except:
                return sentence

        except KeyboardInterrupt:
            return None