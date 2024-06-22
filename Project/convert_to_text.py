import os
import re
import threading
from moviepy.editor import VideoFileClip
import speech_recognition as sr
from pydub import audio_segment , AudioSegment
from textblob import TextBlob
file_lock = threading.Lock()
from logger import logging
import time
import multiprocessing
import requests


max_concurrent_conversion = 5
# Create a semaphore with a count of 5 to limit concurrent downloads
connection_semaphore = threading.Semaphore(max_concurrent_conversion)
video_main_directory = 'video_files' 
text_directory  = 'text_files'



def convert_audio_to_text_file(wav_path,text,filename, text_path):
       
       recognizer = sr.Recognizer()
       with sr.AudioFile(wav_path) as source:
            audio = recognizer.record(source)
            success = 'false'
            try:
                connection_semaphore.release()
                text = recognizer.recognize_google(audio)
                with open(text_path, 'w') as text_file:
                     text_file.write(text)
                print(f'Converted audio from {filename} to text.')
                connection_semaphore.release()
                success = 'true'
            except sr.UnknownValueError:
                print(f"Could not understand audio from {filename}.")
            except sr.RequestError as e:
                print(f"Request error from Google Speech Recognition service for {filename}; {e}")    
            
            file_lock.acquire()
            if success == 'true':
               logging(filename, text, exec_time = 0)
            else:
               text =  text + ' ' + 'download failed'
               filename = ' '
               logging(filename, text ,exec_time = 0)
              
            # Release the lock after writing to the file
            file_lock.release()
           


def thread_text_converter():
 # Create and start threads
 threads = []
 start=time.perf_counter()
 thread_text = 'Parallel converting audio to text using threads'
 videos_thread_path = os.path.join(video_main_directory, 'videos_threads')
 print(f'Checking path: {videos_thread_path}')

 if not os.path.exists(videos_thread_path):
    print(f'Error: Path {videos_thread_path} does not exist')
    return

 print('Starting parallel thread text conversion...')

 for root, dirs, files in os.walk(os.path.join(video_main_directory, 'videos_threads')):
      print(root, dirs, files)
      for filename in files:
        print('a', filename)
        if filename.endswith(".mp3") or filename.endswith(".wav"): 
           audio_path = os.path.join(root, filename)
           base_name = os.path.splitext(filename)[0]
           text_path = os.path.join(root, base_name  + 'en.txt')
           if filename.endswith(".mp3"):
              wav_path = os.path.join(root, base_name + '.wav')
              print('wav_path1' , wav_path)
              AudioSegment.from_mp3(audio_path).export(wav_path, format="wav")
              print('wav_path1' , wav_path)
           else:
              wav_path = audio_path
              print('wav_path2' , wav_path)

           thread = threading.Thread(target=convert_audio_to_text_file, args=(wav_path, thread_text, filename,text_path))
           threads.append(thread)
           thread.start()
    # Wait for all threads to finish
 for thread in threads:
     thread.join()
       
 end=time.perf_counter()
 exec_time = round(end-start,2)  
 filename = ' '
 logging(filename,thread_text,exec_time)
 print(f'videos converted to text files parallely using Threads took {round(end-start,2)} second(s)')


   
if __name__ == "__main__":
 thread_text_converter() 

 


    
    


