import html
import os
import queue
import time

import numpy as np
import sounddevice as sd
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import texttospeech
from google.cloud import translate_v2 as translate
import tkinter as tk
from tkinter import ttk
from threading import Thread

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./genia-hackathon-923da62a3153.json"

speech_client = speech.SpeechClient()
translate_client = translate.Client()
tts_client = texttospeech.TextToSpeechClient()

audio_queue = queue.Queue()
text_queue = queue.Queue()

input_language = "en-US"
output_language = "fr-FR"  
silence_timeout = 17  
last_audio_time = None  
is_running = True  

main_window = None
original_text_box = None
translated_text_box = None
language_options = ["en-US", "fr-FR", "de-DE", "es-ES", "it-IT"]  

def record_audio() -> None:
    """
    Capture audio from the microphone in real-time.

    This function listens to the microphone continuously and processes audio chunks.
    It stores audio data into a queue when the volume exceeds a threshold.
    """
    global last_audio_time, is_running
    last_audio_time = time.time()  

    def audio_callback(indata: np.ndarray, frames: int, time_info: dict, status: sd.CallbackFlags) -> None:
        """
        Callback function that processes audio data and stores it into a queue if
        the audio volume is above a certain threshold.

        Args:
            indata (np.ndarray): Audio input data.
            frames (int): Number of audio frames.
            time_info (dict): Dictionary with time information.
            status (sd.CallbackFlags): Audio stream status.
        """
        global last_audio_time
        if status:
            print(f"Status: {status}")

        volume = np.abs(indata).mean()
        if volume > 0.005:  
            last_audio_time = time.time()  
            audio_queue.put(indata.tobytes())
        else:
            print(f"Low volume: {volume}")

    while is_running:
        with sd.InputStream(samplerate=16000, channels=1, dtype='int16', callback=audio_callback, blocksize=1024, latency="low"):
            while True:
                if last_audio_time and time.time() - last_audio_time > silence_timeout:
                    break
        time.sleep(0.5)  


def stream_recognize() -> None:
    """
    Uses Google Speech-to-Text for real-time streaming transcription.

    This function listens to the audio queue and sends the audio data to Google's
    Speech-to-Text API for transcription. It processes and stores the transcribed text
    in a separate queue for further use.

    Returns:
        None
    """
    def request_generator() -> None:
        """
        Generates audio chunks for streaming recognition.

        This function continuously yields audio chunks from the audio queue to be
        processed by the Speech-to-Text API.

        Yields:
            speech.StreamingRecognizeRequest: Audio chunk to be transcribed.
        """
        while True:
            try:
                chunk = audio_queue.get(timeout=5)  
                yield speech.StreamingRecognizeRequest(audio_content=chunk)
            except queue.Empty:
                break

    while is_running:
        try:
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=input_language,  
                enable_automatic_punctuation=True
            )
            streaming_config = speech.StreamingRecognitionConfig(config=config, interim_results=True)

            responses = speech_client.streaming_recognize(streaming_config, request_generator())
            for response in responses:
                if response.results and response.results[0].is_final:
                    text = response.results[0].alternatives[0].transcript
                    text_queue.put(text)
        except Exception as e:
            time.sleep(1)  


def clean_text(text: str) -> str:
    """
    Decodes HTML entities in the given text and removes leading/trailing whitespace.

    Args:
        text (str): The input text containing HTML entities.

    Returns:
        str: The cleaned text with HTML entities decoded and whitespace removed.
    """
    return html.unescape(text).strip()


def translate_and_speak() -> None:
    """
    Translates the transcribed text and synthesizes the speech in the target language.

    This function fetches the transcribed text from the text queue, translates it using
    the Google Translate API, cleans it, and then synthesizes speech using the
    Google Text-to-Speech API. It plays the audio of the translation in real-time.

    Returns:
        None
    """
    while is_running:
        try:
            text = text_queue.get(timeout=5)  
            if text is None:
                continue

            translation = translate_client.translate(text, target_language=output_language)
            translated_text = translation["translatedText"]
            cleaned_text = clean_text(translated_text)

            update_transcript(text, cleaned_text)

            tts_input = texttospeech.SynthesisInput(text=cleaned_text)
            voice = texttospeech.VoiceSelectionParams(language_code=output_language, ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)
            response = tts_client.synthesize_speech(input=tts_input, voice=voice, audio_config=audio_config)

            audio_array = np.frombuffer(response.audio_content, dtype=np.int16)
            sd.play(audio_array, samplerate=16000)
            sd.wait()

        except queue.Empty:
            pass


def update_transcript(original_text: str, translated_text: str) -> None:
    """
    Updates the text boxes with the original and translated text.

    Args:
        original_text (str): The original transcribed text.
        translated_text (str): The translated text to be displayed.

    Returns:
        None
    """
    global original_text_box, translated_text_box
    if original_text_box is not None and translated_text_box is not None:
        original_text_box.insert(tk.END, f"{original_text}\n")
        translated_text_box.insert(tk.END, f"{translated_text}\n")
        original_text_box.yview(tk.END)
        translated_text_box.yview(tk.END)


def on_language_change(*args) -> None:
    """
    Handles changes in the selected languages from the dropdown menus.

    This function is triggered when the user selects a different language in either the
    original language or translated language dropdown.

    Args:
        *args: Additional arguments from the Combobox event.

    Returns:
        None
    """
    global input_language, output_language

    input_language = original_lang_menu.get()
    output_language = translated_lang_menu.get()

    if input_language == output_language:
        input_language, output_language = output_language, input_language

        original_lang_menu.set(input_language)
        translated_lang_menu.set(output_language)

    print(f"Original language: {input_language}, Translation language: {output_language}")


def start_conversation() -> None:
    """
    Starts the conversation and opens the transcription window.

    This function initializes the Tkinter window, sets up the UI components, and starts
    the threads for audio recording, speech recognition, translation, and speech synthesis.

    Returns:
        None
    """
    global main_window, original_text_box, translated_text_box, is_running, original_lang_menu, translated_lang_menu
    is_running = True
    if main_window is not None:
        main_window.destroy()

    main_window = tk.Tk()
    main_window.title("Real-Time Conversation")
    main_window.geometry("800x600")
    main_window.configure(bg="white")

    frame = tk.Frame(main_window, bg="white")
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    original_label = tk.Label(frame, text="Original Language", font=("Helvetica", 14), fg="#007BFF", bg="white")
    original_label.grid(row=0, column=0, padx=5, pady=5)
    translated_label = tk.Label(frame, text="Translation", font=("Helvetica", 14), fg="#007BFF", bg="white")
    translated_label.grid(row=0, column=1, padx=5, pady=5)

    original_lang_menu = ttk.Combobox(frame, values=language_options, state="readonly", font=("Helvetica", 12))
    original_lang_menu.set(input_language)  # Default value
    original_lang_menu.grid(row=1, column=0, padx=5, pady=5)

    translated_lang_menu = ttk.Combobox(frame, values=language_options, state="readonly", font=("Helvetica", 12))
    translated_lang_menu.set(output_language)  # Default value
    translated_lang_menu.grid(row=1, column=1, padx=5, pady=5)

    original_lang_menu.bind("<<ComboboxSelected>>", on_language_change)
    translated_lang_menu.bind("<<ComboboxSelected>>", on_language_change)

    original_text_box = tk.Text(frame, height=20, width=40, font=("Helvetica", 12), wrap=tk.WORD, bg="lightgrey")
    original_text_box.grid(row=2, column=0, padx=5, pady=5)
    translated_text_box = tk.Text(frame, height=20, width=40, font=("Helvetica", 12), wrap=tk.WORD, bg="lightgrey")
    translated_text_box.grid(row=2, column=1, padx=5, pady=5)

    record_thread = Thread(target=record_audio, daemon=True)
    recognize_thread = Thread(target=stream_recognize, daemon=True)
    translate_thread = Thread(target=translate_and_speak, daemon=True)
    threads = [record_thread, recognize_thread, translate_thread]

    for thread in threads:
        thread.start()

    main_window.mainloop()

if __name__ == "__main__":
    start_conversation()