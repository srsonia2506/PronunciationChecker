import speech_recognition as sr
from pydub import AudioSegment
import numpy as np
from pinyin import pinyin as py_pinyin
from difflib import SequenceMatcher

def get_pitch(signal, sample_rate):
    audio = AudioSegment(signal.tobytes(), frame_rate=sample_rate, sample_width=signal.itemsize, channels=1)
    pitch = audio.dBFS
    return pitch

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def analyze_pronunciation_errors(target_pinyin, user_pinyin):
    target_list = target_pinyin.split()
    user_list = user_pinyin.split()

    errors = []
    for target, user in zip(target_list, user_list):
        if target != user:
            errors.append(f"Expected: {target}, Got: {user}")

    return errors

def provide_feedback(errors):
    if not errors:
        return "Excellent! Your pronunciation is very close to the target word."
    else:
        feedback = "Pronunciation Feedback:\n"
        feedback += "\n".join(errors)
        return feedback

def read_chinese_words(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        chinese_words = [line.strip() for line in file]

    return chinese_words

def main():
    recognizer = sr.Recognizer()

    chinese_words_file = "chinesewords.txt"
    chinese_words = read_chinese_words(chinese_words_file)

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
        #chinese_words = ["你好", "谢谢", "再见"]  
        recognized_text = recognizer.recognize_google(audio_data, language='zh-CN')
        print(f"Recognized Text: {recognized_text}")

        # Get pinyin for recognized text
        recognized_pinyin = py_pinyin.get(recognized_text, format="strip", delimiter=" ")
        print(f"Recognized Pinyin: {recognized_pinyin}")

        # Find the best match based on similarity of pinyin
        best_match = max(chinese_words, key=lambda word: similar(recognized_pinyin, py_pinyin.get(word, format="strip", delimiter=" ")))
        target_pinyin = py_pinyin.get(best_match, format="strip", delimiter=" ")
        similarity_score = similar(recognized_pinyin, target_pinyin)
        print(f"Best Match: {best_match}, Similarity Score: {similarity_score * 100}")

        # Analyze pronunciation errors
        errors = analyze_pronunciation_errors(target_pinyin, recognized_pinyin)

        # Provide detailed feedback to the user
        feedback_message = provide_feedback(errors)
        print(feedback_message)

    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

if __name__ == "__main__":
    main()
