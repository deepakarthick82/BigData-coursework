from pytube import YouTube
import os
import re
import time
import multiprocessing
import requests
import threading
from threading import Semaphore, Lock
from concurrent.futures import ThreadPoolExecutor
from logger import logging
import urllib.parse



# path for the youtube links
path = 'videolinks.txt'
# Specify the folder name for log entry
main_folder_name = "video_files"
os.makedirs(main_folder_name, exist_ok=True)

folder_name = "log_download_output"
file_name = "log.txt"
os.makedirs(folder_name, exist_ok=True)
#define the lock
file_lock = threading.Lock()
max_concurrent_download = 5
# Create a semaphore with a count of 5 to limit concurrent downloads
connection_semaphore = threading.Semaphore(max_concurrent_download)


## This function is used to download the videos for the given link
# and writes to the log file.

def download_video(url, output_path, text):
    # The status is set to True only for parallel execution using threads
    if text != 'Serial_execution': 
     # Acquire the semaphore 
      connection_semaphore.acquire()
     # setting default indicator as 'False' and written to log file only when it is turned to 'True'
   
    try:
        download_successful = False
        encoded_url = urllib.parse.quote(url, safe=':/?=&')
        yt = YouTube(encoded_url)
        yt = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').asc().first()
        format_title = format_filename(yt.title)
        output_file = os.path.join(output_path, f'{format_title}.mp4')
        print(f"Downloading file : {output_file}...")
        subfolder_path = os.path.join(output_path, format_title)
        os.makedirs(subfolder_path, exist_ok=True)
        yt.download(subfolder_path)
        print(f"Downloaded file : {yt.title}")
        download_successful = True
        return download_successful
    except Exception as e:
       print(f"An error occurred: {e}")
       
    finally:
    
     #If semaphore used, then release
     if text != 'Serial_execution':
        # Release the semaphore 
        connection_semaphore.release()
       

     if download_successful == True and text != 'Serial_execution': 
       file_lock.acquire()
       logging(url,text,exec_time = 0)
       file_lock.release()
     elif download_successful == True and text == 'Serial_execution': 
        logging(url,text,exec_time = 0)
     else:
           text =  text + ' ' + 'download failed'
           print(text)
           logging(url, text ,exec_time = 0)

    
# This function builds each url from the given path in the url list.

def get_video_link(path):
    urls = []
    with open(path, 'r') as file:
    # Iterate over each line in the file
      for line in file:
        # Strip whitespace characters from the beginning and end of the line
        video_url = line.strip()
        urls.append(video_url)
    return(urls)

def format_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

#  "downloaded videos folder is created, time initialised"
def serial_downloader():
     video_serial = 'videos_serial'
     sub_video = os.path.join(main_folder_name, video_serial)
     os.makedirs(sub_video, exist_ok=True) 
     start=time.perf_counter()
     urls = get_video_link(path)
     serial_text = 'Serial_execution'
     for url in urls:
       download_successful = download_video(url, sub_video, serial_text)
 
     end=time.perf_counter()
     exec_time = round(end-start,2)  
     url = ' '
     print(exec_time)
     logging(url,serial_text,exec_time)
     print(f'Videos downloaded in Serial took {round(end-start,2)} second(s)') 

def parallel_downloader1():
    start=time.perf_counter()
    processes = []
    videos_parallel1 = "videos_parallel1"
    sub_video  = os.path.join(main_folder_name,videos_parallel1)
    os.makedirs(sub_video, exist_ok=True) 
    parallel1_text = 'multi processing'
    urls = get_video_link(path)
    for url in urls:
        p = multiprocessing.Process(target=download_video,args=[url,sub_video, parallel1_text])
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
    end=time.perf_counter()
    exec_time = round(end-start,2) 
    url = ' ' 
    logging(url,parallel1_text,exec_time)
    print(f'videos downloaded Parallelly using multiprocessing took {round(end-start,2)} second(s)')

def thread_downloader():
 # Create and start threads
 threads = []
 start=time.perf_counter()
 videos_threads = "videos_threads"
 sub_video  = os.path.join(main_folder_name,videos_threads)
 os.makedirs(sub_video, exist_ok=True) 
 threads_text = 'Parallel execution using threads'
 urls = get_video_link(path)
 for url in urls:
     thread = threading.Thread(target=download_video, args=(url,sub_video,threads_text))
     threads.append(thread)
     thread.start()
    # Wait for all threads to finish
 for thread in threads:
    thread.join()
       
 end=time.perf_counter()
 exec_time = round(end-start,2) 
 url = '' 
 logging(url, threads_text, exec_time)
 print(f'videos downloaded parallely using Threads took {round(end-start,2)} second(s)') 


def parallel_downloader2():
    start=time.perf_counter()
    output_directory = "downloaded_videos_parallel2"
    urls = get_video_link(path)
    parallel2_text = 'Parallel execution using Threadpool executor'
    #Setting the max_workers as 5 so that only 5 threads are active at a time.
    with ThreadPoolExecutor(max_workers=max_concurrent_download) as executor:
      futures = [executor.submit(download_video, url, output_directory, parallel2_text) for url in urls]
      for future in futures:
            future.result()  # Wait for all downloads to complete

    end=time.perf_counter()
    exec_time = round(end-start,2)  
    url =''
    logging(url,parallel2_text,exec_time)
    print(f'Videos downloaded Parallelly (ThreadPoolExecutor): {end-start} second(s)')


  

if __name__ == "__main__":
 #serial_downloader()
 #parallel_downloader1()
 parallel_downloader2()
 #thread_downloader()