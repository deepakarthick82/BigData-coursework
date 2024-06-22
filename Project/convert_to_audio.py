import os
import re
import threading
from moviepy.editor import VideoFileClip
import speech_recognition as sr
from pydub import audio_segment , AudioSegment
from textblob import TextBlob
from concurrent.futures import ThreadPoolExecutor
file_lock = threading.Lock()
from logger import logging
import time
import multiprocessing
import requests

max_concurrent_conversion = 5
# Create a semaphore with a count of 5 to limit concurrent downloads
connection_semaphore = threading.Semaphore(max_concurrent_conversion)
video_main_directory = 'video_files'

folder_name = "log_download_output"
file_name = "log.txt"
os.makedirs(folder_name, exist_ok=True)

def convert_video_to_audio_file(video_path, audio_path,text,filename):

  if text != 'Serial_audio conversion':   
     connection_semaphore.acquire()
     
  try:
        conversion_succesful = False
        # Load the video file
        video_clip = VideoFileClip(video_path)
        
        # Extract the audio
        audio_clip = video_clip.audio
        
        # Write the audio file
        audio_clip.write_audiofile(audio_path)
        conversion_succesful = True
  except Exception as e:
        print(f"An error occurred during video processing: {e}")
        raise  # Re-raise the exception after handling if needed
  finally:
        if text != 'Serial_audio conversion':
            connection_semaphore.release()

  if conversion_succesful == True and text != 'Serial_audio conversion': 
       file_lock.acquire()
       logging(filename,text,exec_time = 0)
       file_lock.release()
  elif conversion_succesful == True and text == 'Serial_audio conversion': 
        logging(filename,text,exec_time = 0)
  else:
           text =  text + ' ' + 'download failed'
           logging(filename, text ,exec_time = 0)

  

   
def thread_audio_converter():
 # Create and start threads
 threads = []
 start=time.perf_counter()
 videos_thread_path = os.path.join(video_main_directory, 'videos_threads')
 thread_text = 'parallel audio conversion using threads'
 print(f'Checking path: {videos_thread_path}')

 if not os.path.exists(videos_thread_path):
    print(f'Error: Path {videos_thread_path} does not exist')
    return

 print('Starting parallel thread audio conversion...')

 for root, dirs, files in os.walk(os.path.join(video_main_directory, 'videos_threads')):
      print(root, dirs, files)
      for filename in files:
        if filename.endswith(".mp4") or filename.endswith(".mkv") or filename.endswith(".webm"):  
           video_path = os.path.join(root, filename)
           base_name = os.path.splitext(filename)[0]
           # Define the audio path in the same folder as the video
           audio_path = os.path.join(root, base_name + '.wav')
           thread = threading.Thread(target=convert_video_to_audio_file, args=(video_path,audio_path,thread_text,filename))
           threads.append(thread)
           thread.start()
            # Wait for all threads to finish
 for thread in threads:
    thread.join()
       
 end=time.perf_counter()
 exec_time = round(end-start,2)  
 filename = ' '
 logging(filename,thread_text,exec_time)
 print(f'videos converted to audio files parallely using Threads took {round(end-start,2)} second(s)')

  

def parallel1_audio_conversion():
    start=time.perf_counter()
    parallel1_text = 'Parallel audio conversion using Threadpool executor'
    videos_parallel1_path = os.path.join(video_main_directory, 'videos_parallel1')
    path = []
    print(f'Checking path: {videos_parallel1_path}')

    if not os.path.exists(videos_parallel1_path):
        print(f'Error: Path {videos_parallel1_path} does not exist')
        return

    print('Starting parallel audio conversion...')


    for root, dirs, files in os.walk(os.path.join(video_main_directory, 'videos_parallel1')):
      print(root, dirs, files)
      for filename in files:
        if filename.endswith(".mp4") or filename.endswith(".mkv") or filename.endswith(".webm"):  
           video_path = os.path.join(root, filename)
           base_name = os.path.splitext(filename)[0]
           # Define the audio path in the same folder as the video
           audio_path = os.path.join(root, base_name + '.wav')
           path.append((video_path, audio_path, filename))

    with ThreadPoolExecutor(max_workers=max_concurrent_conversion) as executor:
         futures = [executor.submit(convert_video_to_audio_file, video_path,audio_path,parallel1_text,filename) for video_path, audio_path, filename in path]
         for future in futures:
             future.result()  # Wait for all downloads to complete

    end=time.perf_counter()
    exec_time = round(end-start,2)  
    url =''
    logging(url,parallel1_text,exec_time)
    print(f'Videos converted to audiofiles Parallelly (ThreadPoolExecutor): {end-start} second(s)')

    
def serial_audio_converter():
 start=time.perf_counter()
 serial_text = 'Serial_audio conversion'
 # Ensure that the main directory and the videos_serial directory are correct
 videos_serial_path = os.path.join(video_main_directory, 'videos_serial')
 print(f'Checking path: {videos_serial_path}')

 if not os.path.exists(videos_serial_path):
        print(f'Error: Path {videos_serial_path} does not exist')
        return

 print('Starting serial audio conversion...')


 for root, dirs, files in os.walk(os.path.join(video_main_directory, 'videos_serial')):
     print(root, dirs, files)
     for filename in files:
       if filename.endswith(".mp4") or filename.endswith(".mkv") or filename.endswith(".webm"):  
           video_path = os.path.join(root, filename)
           base_name = os.path.splitext(filename)[0]
           # Define the audio path in the same folder as the video
           audio_path = os.path.join(root, base_name + '.wav')
           convert_video_to_audio_file(video_path,audio_path,serial_text,filename)

 end=time.perf_counter()
 exec_time = round(end-start,2)  
 filename = ' '
 logging(filename,serial_text,exec_time)
 print(f'Videos converted to audio took {round(end-start,2)} second(s)')    


      
  
if __name__ == "__main__":
 
 serial_audio_converter()
 thread_audio_converter()
 parallel1_audio_conversion()
