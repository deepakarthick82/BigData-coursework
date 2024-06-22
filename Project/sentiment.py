import os
import time
import speech_recognition as sr
from textblob import TextBlob
from googletrans import Translator
import spacy,nltk
from nrclex import NRCLex
nlp = spacy.load('en_core_web_sm')
nltk.download('punkt')

import threading
file_lock = threading.Lock()
from threading import Semaphore, Lock
from logger import logging


def cal_sentiment_analysis(text, filename,senti_path, thread_text):
    try:
       with open(senti_path, 'w', encoding='utf-8') as senti_text_file:
            success = 'true'
            try:
              print('test reached here')
              blob = TextBlob(text)
              sentiment = blob.sentiment
              print(f'Calculated scores for: "{filename}"', file = senti_text_file)
              print(f'   Sentiment: {blob.sentiment}"', file = senti_text_file)
              print(f'   Polarity: {blob.sentiment.polarity}"', file = senti_text_file)
              print(f'   Subjectivity: {blob.sentiment.subjectivity}"', file = senti_text_file)
            
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
        print(f"Error handling file {senti_path}: {e}") 
     
     
     
           


def thread_sentimentcal():
  start=time.perf_counter()
  video_main_directory = 'video_files'
  # Create and start threads
  threads = []
  thread_text = 'sentiment analysis using threads'
  videos_thread_path = os.path.join(video_main_directory, 'videos_threads')
  print(f'Checking path: {videos_thread_path}')

  if not os.path.exists(videos_thread_path):
    print(f'Error: Path {videos_thread_path} does not exist')
    return

  print('Starting parallel thread text conversion...')

  for root, dirs, files in os.walk(os.path.join(video_main_directory, 'videos_threads')):
      print(root, dirs, files)
      for filename in files:
         if filename.endswith(".txt") :
           file_path = os.path.join(root, filename)
           base_name = os.path.splitext(filename)[0]
           senti_path = os.path.join(root, base_name  + '_senti' +'.txt')
            
           with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            thread = threading.Thread(target=cal_sentiment_analysis, args=(text, filename,senti_path,thread_text))
            threads.append(thread)
            thread.start()
    # Wait for all threads to finish
  for thread in threads:
       thread.join()
       
  end=time.perf_counter()
  exec_time = round(end-start,2)  
  filename = ' '
  logging(filename,thread_text,exec_time)
  print(f'sentiment calculation  done parallely using Threads took {round(end-start,2)} second(s)')





if __name__ == "__main__":
 
 thread_sentimentcal()
