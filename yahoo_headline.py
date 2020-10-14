# -*- coding: utf-8 -*-
# yahoo_headline.py

import warnings
from gtts import gTTS
import json
import re
import os
import sys
import requests
import urllib.request
from selenium import webdriver
import time
from datetime import datetime

def get_second_url(first_url): 
  fixed_part1 = 'class="pickupMain_articleInfo"><a href="'
  fixed_part2 = '" data-ylk="rsec:tpc_main;slk:headline;pos:1;targurl'
  link_url = ''
  while True:
    try:
      fd = urllib.request.urlopen(first_url)
    except (IOError):
      print ('Exception. Sleep 30 sec.') # 
      time.sleep(30)
      print ('Now try again...') # until here
      continue
    else:
      line = fd.readline()
      #print (line.decode('utf-8')) # debug
      while line:
        raw_text = line.decode('utf-8')
        if b'class="pickupMain_articleInfo"><a href="' in line:
          link_url = raw_text.split(fixed_part2)[0].split(fixed_part1)[1]
          #print (link_url) # debug
          break
        line = fd.readline()
      #continue
      break
  return link_url

def get_article(target_html): # str
  #print (target_html)
  fixed_part1 = '<title>' # title head
  fixed_part2 = ' - Yahoo!ニュース</title>' # title last
  fixed_part3 = 'yjDirectSLinkTarget">' # body head
  fixed_part4 = '【関連記事】' # body end mark
  fixed_part5 = '<!-- 本文表示可能 -->' # body head2
  fixed_part6 = '■関連' # body end mark2
  fixed_part7 = '<div class="group group-firstHalf">' # body head3
  fixed_part8 = '後半を読む' # body last3

  title_text = target_html.split(fixed_part2)[0].split(fixed_part1)[1].replace("　","。").replace(" ","。")
  #print (target_html.split(fixed_part4)[0]) # debug
  if fixed_part3 in target_html and fixed_part4 in target_html:
    body_text = target_html.split(fixed_part4)[0].split(fixed_part3, 1)[1]
  elif fixed_part5 in target_html and fixed_part6 in target_html:
    body_text = target_html.split(fixed_part6)[0].split(fixed_part5, 1)[1]
  else:
    date_time = datetime.now().strftime('%y%m%d%H%M%f') 
    tmp_filename = 'error_report' + date_time +  '.html'
    with open(tmp_filename, 'wb') as f:
      f.write(target_html.encode())
    return "ワーオ。エラーが発生しちゃったみたい。ログファイルを見て解析してください。だっちゃ。"

  article_text = title_text + "。" + body_text
  article_text = re.sub(r'<a href=.*?</a>',"", article_text)
  article_text = re.sub(r'（[ぁ-ん]+）',"", article_text) # re.sub(r'(?<=（)[ぁ-ん](?=）)',"", article_text) # http://www-creators.com/archives/5462
  article_text = re.sub(r'<[^<]+>',"", article_text).replace("\n",'').replace("＝",'').replace("=",'').replace("～",'').rstrip() + "\n"
  return article_text

def gen_sound_file(mytext): # call gTTS and make voice sound file
  language = "ja"
  myobj = gTTS(text=mytext, lang=language, slow=False)
  myobj.save("tmp.mp3")
  #os.system("mplayer -speed 1.3 -af scaletempo tmp.mp3") # ORG - truncated the sound file
  os.system("mplayer  -af scaletempo=scale=1.2:speed=none -speed 1.3 tmp.mp3") # Exeriment
  #return (file_name)

#----------- main ---------------------
warnings.simplefilter('ignore') # Disable warinngs
fixed_part1 = '=;"><a href="' # 'newstop=;"><a href="'
fixed_part2 = '" data-ylk="rsec:tpc_maj;slk:title;pos:'
fixed_part3 = '" data-ylk="rsec:tpc_maj;slk:title;pos:8;'
fixed_part01 = '</a></li></ul><div class="topicsList_button">'
fixed_part02 = 'data-ual-gotocontent="true">'
fixed_part03 = '</a></li><li class='
org_url = 'https://news.yahoo.co.jp/'

while True:
  try:
    fd = urllib.request.urlopen(org_url)
  except (IOError):
    print ('Exception. Sleep 30 sec.') # 
    time.sleep(30)
    print ('Now try again...') # until here
    continue
  else:
    line = fd.readline()
    #print (line) # debug
    while line:
      raw_text = line.decode('utf-8')
      if b'<h2 class="topics_title">' in line:
        raw_part1 = raw_text.split(fixed_part3)[0].split(fixed_part1)
        raw_part2 = raw_text.split(fixed_part01)[0].split(fixed_part02)
        break
      line = fd.readline()
    break
url_list = []
topic_list = []
for i in range(1, 9):
  #print (raw_part1[i]), (fixed_part2) # debug loop uncomment when raw_part[i] is not loaded as expected 
  url_list.append(raw_part1[i].split(fixed_part2)[0])
  temp_line = re.sub(r'<span .*?</span>',"", raw_part2[i])
  topic_list.append(temp_line.split(fixed_part03)[0])
  print (str(i) +'. ' + topic_list[i-1])

topics = []
#val = input('読み上げてほしい番号を入力（単一）')
#topics.append(int(val))
while True:
  val = input('\n読み上げてほしい番号を一つずつ入力（0で終了）') # Enter the number for read aloud one at a time, enter 0 to finish
  if val == '0':
    print('入力終了')
    break
  topics.append(int(val))

#-----------------------------------
#get_second_url 
url2_list = []
#for topic_url in url_list:
for topic_num in topics:
  tmp_url = get_second_url(url_list[topic_num-1])
  url2_list.append(tmp_url)

#-----------------------------------
driver = webdriver.PhantomJS()

temp_text = ''
count = 1
for topic_url in url2_list:
  driver.get(topic_url)
  html = driver.page_source
  article_text = get_article (html)
  if count  == 1:
    temp_text = article_text
  else:
    temp_text = temp_text + "\n\n" + article_text
  if count  > 0: # DEBUG e.g.: count  == 2, org: > 0
    #print (topics[count-1]); print (article_text) # DEBUG
    gen_sound_file(article_text)
    count = count + 1
  else:
    count = count + 1
driver.quit()
#tmp_filename = 'test_temp.txt'    # Uncomment this block for debug
#with open(tmp_filename, 'wb') as f:
#  f.write(temp_text.encode())



