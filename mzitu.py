#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import requests
import os, sys
from bs4 import BeautifulSoup
import threading
import time

savepath='D:/meizitu/'

Hostreferer = {
    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
    'Referer': 'http://www.mzitu.com'
}

ids = []
autoAgree = False

dirname, filename = os.path.split(os.path.abspath(__file__))
savefile=dirname+"/ids"
if os.path.isfile("ids"):
   exist = input("發現存檔，是否繼續?")
   if exist[0] != 'Y':
       with open(savefile, 'r') as f:           
           ids=f.readline().split()
           autoAgree = True


if len(sys.argv) == 1:
    if not autoAgree:
        ids.extend(input('請輸入ID：').split())
else:
    ids.extend(sys.argv[1:])
with open(savefile, 'w') as f:
    for id in ids:
        f.write(id+" ")

download_num = 0
def download(url,filename,i):
    global download_num 

    success=False
    while not success :
        try:
            if not os.path.isfile(filename):                    
                r = requests.get(url, headers = Hostreferer)   
                soup = BeautifulSoup(r.text, "html.parser")
                main_img = soup.find('div', 'main-image').img.get('src')
                res = requests.get(main_img, headers=Hostreferer)
                if res.status_code == 200:
                    with open(filename, 'wb') as f:
                        f.write(res.content)
                        success = True
                        print(i, end=" ", flush = True)
            else:     
                success = True       
                print('['+str(i), end="] ", flush = True)
        except (KeyboardInterrupt, SystemExit):
            input("\nInterrupted "+ str(i))                            
            exit()
        except:
            print("\nGet " + str(i) + " error, retry...")
    download_num = download_num - 1

for id in ids:
    
    start_url = 'https://www.mzitu.com/' + id

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
    title =  id+"-"+soup.find('h2','main-title').text

    print(title+" 共"+ str(maxpage) +"張圖")
    path = savepath+title
    try:
        # Create target Directory
        os.mkdir(path)
        print("目錄:" , path ,  " 已建立") 
    except FileExistsError:
        if not autoAgree:               
            exist = input("目錄:" + path + " 已存在，是否繼續?(Y/N/A)").upper()
            if exist[0] == 'A':
                autoAgree = True
            else:    
                if exist[0] != 'Y':
                    continue

    for i in range(1, maxpage + 1):        
        while download_num >=4:
            time.sleep(1)
        filename = path+"/"+str(i)+".jpg"
        url=start_url+'/'+str(i)
        download_num = download_num + 1
        t = threading.Thread(target = download, args = (url,filename,i,))
        t.start()
    while download_num != 0:
        time.sleep(1)                
    print("")
    print("============================")
os.remove(savefile)
input("Press Enter to continue...")
exit()