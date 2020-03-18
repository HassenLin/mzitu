#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import requests
import os, sys
from bs4 import BeautifulSoup
import threading
import time

savepath_default = 'D:/meizitu/' # if script put in d:/path/code, will download to d:/path
baseurl ='https://www.mzitu.com/' 

Hostreferer = {
    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
    'Referer': baseurl
}

pathChars = "\\/`*{}[]()<|>-!$:'\""
ids = set([])
autoAgree = False
autoDisagree = False
download_num = 0
    
dirname, filename = os.path.split(os.path.abspath(__file__))

savepath = savepath_default
dirname1, filename1 = os.path.split(os.path.abspath(dirname))
if filename1 == "code":
   savepath=dirname1.replace('\\','/')+"/"

savefile=dirname+"/ids"
if os.path.isfile(savefile):
   exist = input("發現存檔，是否繼續?").upper()
   if len(exist)>0  and exist[0] == 'Y':
       with open(savefile, 'r', encoding="UTF-8") as f:           
           ids.update(f.readline().split())
           autoAgree = True

if len(sys.argv) == 1:
    if not autoAgree:
        ids.update(input('請輸入ID：').split())
else:
    ids.update(sys.argv[1:])

downloaded_ids = set([])
history = savepath+"history.txt"

completed_ids = set([])
if os.path.isfile(history):
    with open(history, 'r', encoding="UTF-8") as f:  
        for line in f:         
            completed_id=line.split("-")[0]
            if completed_id.isdigit():
                completed_ids.add(completed_id)

for d in os.listdir(savepath):
    if os.path.isdir(savepath+d):
        downloaded_id=d.split("-")[0]
        if downloaded_id.isdigit():
            downloaded_ids.add(downloaded_id)

def download(url,filename,i):
    global download_num 
    error_cnt=0
    success=False
    while not success :
        try:
            r = requests.get(url, headers = Hostreferer)   
            soup = BeautifulSoup(r.text, "html.parser")
            main_img = soup.find('div', 'main-image').img.get('src')
            res = requests.get(main_img, headers=Hostreferer)
            if res.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(res.content)
                    success = True
                    print(i, end=" ", flush = True)

        except (KeyboardInterrupt, SystemExit):
            input("\nInterrupted "+ str(i))                            
            exit()

        except:            
            if error_cnt > 3:
                print("\nGet " + str(i) + " error, delay 10 secounds.")
                time.sleep(10)
            print("\nGet " + str(i) + " error, retry...")                

        error_cnt = error_cnt + 1
    download_num = download_num - 1

def GetPhotoByIds(ids):
    global download_num, autoAgree, autoDisagree, savepath, savefile, baseurl, pathChars 

    with open(savefile, 'w', encoding="UTF-8") as f:
        for id in ids:
            f.write(id+" ")    
    for id in ids:
        if id in completed_ids:
            print("先前已完成，略過 "+id)
            continue
        if id in downloaded_ids:
            if autoDisagree:
                print("略過 "+id)
                continue
            if not autoAgree:               
                exist = input("id:" + id + " 已存在，是否繼續?(Y/N/A/NA)").upper()
                if len(exist)>0  and exist[0] == 'A':
                    autoAgree = True
                elif len(exist)>=2 and exist[0] == 'N' and exist[1] == 'A':
                    autoDisagree = True
                    print("略過 "+id)
                    continue
                else:    
                    if len(exist) == 0 or exist[0] != 'Y':
                        print("略過 "+id)
                        continue

        start_url = baseurl + id

        r = requests.get(start_url, headers=Hostreferer)

        if r.status_code != 200:
            print(start_url+" 錯誤")    
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        pages = soup.find('div', 'pagenavi').find_all('span')
        maxpage = 1
        for page in pages:
            if page.text.isdigit():
                if maxpage < int(page.text):
                    maxpage = int(page.text)

        ptitle=soup.find('h2','main-title').text
        
        for c in pathChars:
            if c in ptitle:
                ptitle = ptitle.replace(c, " ")            
        title = id+"-"+ptitle

        print(title+" 共"+ str(maxpage) +"張圖")
        path = savepath+title
        try:
            # Create target Directory
            os.mkdir(path)
            print("目錄:" , path ,  " 已建立") 
        except FileExistsError:
            print("目錄:" , path ,  " 已存在") 

        for i in range(1, maxpage + 1):        
            while download_num >=4:
                time.sleep(1)
            filename = path+"/"+str(i)+".jpg"
            if not os.path.isfile(filename):                     
                url=start_url+'/'+str(i)
                download_num = download_num + 1
                t = threading.Thread(target = download, args = (url,filename,i,))
                t.start()
            else:     
                print('['+str(i), end="] ", flush = True)

        while download_num != 0:
            time.sleep(1)
        completed_ids.add(id)
        with open(history, 'a', encoding="UTF-8") as f:
            f.write(title+'\n')          
        print("")
        print("============================")
        
    os.remove(savefile)

if len(ids) > 0 :
    GetPhotoByIds(ids)
else:
    for page in range(1,243):
        print("**********************************")
        print("  Get page:" + str(page))
        print("**********************************")
        page_url = baseurl+"page/"+str(page)+"/"
        r = requests.get(page_url, headers=Hostreferer)

        if r.status_code != 200:
            print(page_url+" 錯誤")    
            continue
        ids.clear()
        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.find_all('a')
        for link in links:
            href=link.get("href")
            if href.startswith(baseurl):
                 id = href[len(baseurl):]                 
                 if id.isdigit():
                    #  print(id)
                     ids.add(id)
        if len(ids) > 0 :
             GetPhotoByIds(ids)             


input("Press Enter to continue...")
exit()