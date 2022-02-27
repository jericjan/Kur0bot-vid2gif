from flask import Flask, cli, request
from threading import Thread
import os
import re
# import sys
import requests
import uuid
import subprocess
import glob
import shutil
from tqdm import tqdm
from datetime import datetime, timedelta
import io
from ratelimiter import RateLimiter
rate_limiter = RateLimiter(max_calls=1, period=1)

cli.show_server_banner = lambda *_: None
app = Flask("")
pbar_list = []

@app.route("/")
def home():
    return "Hello. I am alive!"

def updatebar(edit_url,headers):
  with rate_limiter:
    payload = {'content' : pbar_list[-1] }
    requests.patch(
    edit_url, payload,headers=headers
    )      
@app.route("/gif")
def gif():
    
    uuid_id = uuid.uuid4()
    link = request.args.get('url')
    channel_id = request.args.get("channel_id")
    msg_id = request.args.get("msg_id")
    headers = {"Authorization": f"Bot {os.getenv('TOKEN')}"}
    send_url = f"https://discord.com/api/v9/channels/{channel_id}/messages"  
    edit_url = f"https://discord.com/api/v9/channels/{channel_id}/messages/{msg_id}"


    filename = link.split("/")[-1]    
    new_filename = ''.join(filename.split('.')[:-1])+".gif"
    print(f"filename:{filename}\nGif name:{new_filename}")
    if re.search(r".+\.mp4|.+\.mkv|.+\.mov|.+\.webm", filename) is not None:
                # r = requests.get(link)          
                # vid = io.BytesIO(r.content)
                # vid.seek(0)
                frames_folder = f"frames_{uuid_id}"
                os.mkdir(f"{frames_folder}/")
                frames_path = f"{frames_folder}/frame%04d.png"

                coms = [
                    "ffmpeg",
                    "-i",
                    link,
                    frames_path
                ]                
                process = subprocess.Popen(
                    coms,stdout=subprocess.PIPE, stderr=subprocess.STDOUT,universal_newlines=True
                )
                #stdout, stderr = process.communicate()
                full_line = ""
                pbar = tqdm(total=100)
                for line in process.stdout:
                      if not line:
                          break
                      # print(line.decode('utf-8'))
                      linedec = line
                      full_line += linedec
                      # print(linedec)
                      if (
                          re.search(r"(?<=Duration: )\d{2}:\d{2}:\d{2}.\d{2}", full_line)
                          is not None
                      ):
                          duration_str = re.findall(
                              r"(?<=Duration: )\d{2}:\d{2}:\d{2}.\d{2}", full_line
                          )[-1]
                          # print(f"Duration is {duration_str}")
                          strpcurr = datetime.strptime(duration_str, "%H:%M:%S.%f")
                          duration = timedelta(
                              hours=strpcurr.hour,
                              minutes=strpcurr.minute,
                              seconds=strpcurr.second,
                              microseconds=strpcurr.microsecond,
                          )
                      if (
                          re.search(r"(?<=time=)\d{2}:\d{2}:\d{2}.\d{2}", full_line)
                          is not None
                      ):
                          # print(linedec)
                          if (
                              re.findall(r"(?<=time=)\d{2}:\d{2}:\d{2}.\d{2}", full_line)[-1]
                              != "00:00:00.00"
                          ):
                              currtime_str = re.findall(
                                  r"(?<=time=)\d{2}:\d{2}:\d{2}.\d{2}", full_line
                              )[-1]
                              # print(f"Current time is {currtime_str}")
                              strpcurr = datetime.strptime(currtime_str, "%H:%M:%S.%f")
                              currtime = timedelta(
                                  hours=strpcurr.hour,
                                  minutes=strpcurr.minute,
                                  seconds=strpcurr.second,
                                  microseconds=strpcurr.microsecond,
                              )
                              # print(linedec)
                              try:
                                  percentage = (
                                      currtime.total_seconds() / duration.total_seconds()
                                  ) * 100
                                  # print(f"{percentage}% complete...")
      
                                  output = io.StringIO()
                                  pbar = tqdm(total=100, file=output, ascii=False)
                                  pbar.update(float(f"{percentage:.3f}"))
                                  pbar.close()
                                  final = output.getvalue()
                                  output.close()
                                  final1 = final.splitlines()[-1]
                                  # print(final1)
                                  aaa = re.findall(
                                      r"(?<=\d\%)\|.+\| (?=\d+|\d+.\d+/\d+|\d+.\d+)", final1
                                  )[0]
                                  pbar_list.append(
                                      f"Extracting frames...\n{round(percentage, 2)}% complete...\n`{aaa}`<a:ameroll:941314708022128640>"
                                  )
                                  updatebar(edit_url,headers)
                              except:
                                if not filename.endswith('gif'):
                                  with rate_limiter:
                                    payload = {'content' : "Uh, I couldn't find the duration of vod. idk man." }
                                    requests.patch(
                                    edit_url, payload,headers=headers
                                    )                                    





                  
                print("FFMPEGGGG")
                gif_ski_frames_path = f"{frames_folder}/frame*.png"
                gif_ski_frames_path = glob.glob(gif_ski_frames_path)
               # gif_ski_frames_path = ' '.join(gif_ski_frames_path)                                
                with rate_limiter:
                  payload = {'content' : 'Making gif...' }
                  requests.patch(
                  edit_url, payload,headers=headers
                  )      
                coms = [
                    "gifski_/gifski",
                    "-W",
                    "480",
                    "--output",
                    new_filename
                ]
                coms = coms + gif_ski_frames_path
                #print(shlex.join(coms))
                process = subprocess.Popen(
                    coms,stdout=subprocess.PIPE,                                           stderr=subprocess.STDOUT,universal_newlines=True
                )
                for line in process.stdout:
                  with rate_limiter:
                    payload = {'content' : f'Making gif...\n{line}' }
                    requests.patch(
                    edit_url, payload,headers=headers
                    )                       
                stdout, stderr = process.communicate()
                print("GIFSKI")          
                # vid.close()
                with rate_limiter:
                  payload = {'content' : 'Sending...' }
                  requests.patch(
                  edit_url, payload,headers=headers
                  )          
                try:        
                  with rate_limiter:
                      payload = {'files[0]': (new_filename, open(new_filename, 'rb')) }
                      r = requests.post(
                      send_url, files=payload,headers=headers
                      )                      
                except Exception as e:
                    with rate_limiter:
                      payload = {'content' : 'Too large for server. Sending somewhere else..' }
                      requests.patch(
                      edit_url, payload,headers=headers
                      )                    
                  # if e.status == 413:
                    coms = ['curl','--upload-file',new_filename,f"https://transfer.sh/{new_filename}"]
                    process = subprocess.Popen(
                        coms,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                    stdout, stderr = process.communicate()  
                    link = stdout.decode('utf-8').splitlines()[-1]
                    with rate_limiter:
                      payload = {'content' : link }
                      requests.patch(
                      edit_url, payload,headers=headers
                      )  
                os.remove(new_filename)
                shutil.rmtree(f"{frames_folder}/")    
  
    return "GIFFIFIED!"

@app.route("/test")
def test():
    headers = {"Authorization": f"Bot {os.getenv('TOKEN')}"}
    request_url = "https://discord.com/api/v9/channels/809247468084133898/messages"
    payload = {'files[0]': ('pogger.jpg', open('cover4.jpg', 'rb')) }
    r = requests.post(
    request_url, files=payload,headers=headers
    )   
    print(r.status_code)
    print(r.content)
    return 'pogger'
  
def run():
      app.run(host="0.0.0.0", port=8081)



def keep_alive():
    t = Thread(target=run)
    t.start()
