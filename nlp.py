import speech_recognition as sr
import pyaudio
import numpy as np
from pinyin import pinyin as py_pinyin
from difflib import SequenceMatcher

def get_pitch(signal, sample_rate):
    from pydub import AudioSegment

    audio = AudioSegment(signal.tobytes(), frame_rate=sample_rate, sample_width=signal.itemsize, channels=1)
    pitch = audio.dBFS
    return pitch

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def main():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Say something in Chinese:")
        audio_data = recognizer.listen(source)

    try:
        # Perform pitch modulation analysis
        sample_rate = audio_data.sample_rate
        signal = np.frombuffer(audio_data.frame_data, dtype=np.int16)
        pitch = get_pitch(signal, sample_rate)
        print(f"Pitch: {pitch} dBFS")

        # Chinese pronunciation evaluation
        chinese_words = ["你好", "谢谢", "再见"]  
        recognized_text = recognizer.recognize_google(audio_data, language='zh-CN')
        print(f"Recognized Text: {recognized_text}")

        best_match = max(chinese_words, key=lambda word: similar(recognized_text, py_pinyin(word, style=1)[0]))
        similarity_score = similar(recognized_text, py_pinyin(best_match, style=1)[0])
        print(f"Best Match: {best_match}, Similarity Score: {similarity_score}")

    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

if __name__ == "__main__":
    main()
