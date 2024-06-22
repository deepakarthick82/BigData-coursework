import os
import speech_recognition as sr
import spacy,nltk
from nrclex import NRCLex
nlp = spacy.load('en_core_web_sm')
nltk.download('punkt')
import threading
from threading import Semaphore, Lock
import time
from logger import logging
file_lock = threading.Lock()

def extract_emotions(text, filename,emotion_path,thread_text):
   try:
      with open(emotion_path, 'w', encoding='utf-8') as emotion_text_file:
           success = 'true'
           try:

            doc = nlp(text)
            full_text = ' '.join([sent.text for sent in doc.sents])
            emotion = NRCLex(text)
            print(f'Detected Emotions and Frequencies for {filename}:')
            print(f'Emotions: {emotion.affect_frequencies}',file = emotion_text_file) 
            
     
           except Exception as e:
                print(f"Error during sentiment analysis for {filename}: {e}")
                success = 'false'
 
      file_lock.acquire()
      try:
          if success == 'true':
               logging(filename, thread_text, exec_time = 0)
          else:
               text =  text + ' ' + 'download failed'
               filename = ' '
               logging(filename, thread_text ,exec_time = 0)
      finally:           
            # Release the lock after writing to the file
            file_lock.release()
            
   except Exception as e:
      print(f"Error handling file {emotion_path}: {e}") 
     
     


def thread_extract_emotions():
  threads = []
  start=time.perf_counter()
  video_main_directory = 'video_files'
  thread_text = 'emotion extracted using threads'
  videos_thread_path = os.path.join(video_main_directory, 'videos_threads')
  print(f'Checking path: {videos_thread_path}')

  if not os.path.exists(videos_thread_path):
    print(f'Error: Path {videos_thread_path} does not exist')
    return

  print('Starting parallel thread emotion extraction...')
  
  for root, dirs, files in os.walk(os.path.join(video_main_directory, 'videos_threads')):
      print(root, dirs, files)
      for filename in files:
         if filename.endswith("en.txt"):
           file_path = os.path.join(root, filename)
           base_name = os.path.splitext(filename)[0]
           emotion_path = os.path.join(root, base_name  + '_emotions' +'.txt')
           with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            thread = threading.Thread(target=extract_emotions, args=(text, filename,emotion_path,thread_text))
            threads.append(thread)
            thread.start() 

  for thread in threads:
      thread.join()
       
  end=time.perf_counter()
  exec_time = round(end-start,2)  
  filename = ' '
  logging(filename,thread_text,exec_time)
  print(f'Emotions extracted parallely using Threads took {round(end-start,2)} second(s)')




          
if __name__ == "__main__":
 thread_extract_emotions()