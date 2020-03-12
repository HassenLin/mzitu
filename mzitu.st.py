#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import requests
import os, sys
from bs4 import BeautifulSoup


savepath='D:/meizitu/'

Hostreferer = {
    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
    'Referer': 'http://www.mzitu.com'
}

ids = []
autoAgree = False
if len(sys.argv) == 1:
    ids = input('請輸入ID：').split()
else:
    ids = sys.argv[1:]
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
        success=False
        while not success :
            try:
                filename = path+"/"+str(i)+".jpg"
                if not os.path.isfile(filename):                    
                    r = requests.get(start_url+'/'+str(i), headers = Hostreferer)   
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
                input("\nInterrupted, press Enter to continue...")                            
                exit()
            except:
                print("\nGet " + str(i) + " error, retry...")
    print("")
    print("============================")
input("Press Enter to continue...")
exit()