# pypt.py
# author:cai-yang
#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import urllib
import urllib.request
import re
import os
import time

cookie=''
useragent=''

def GetSearchUrl(keyword):
    baseurl='https://pt.sjtu.edu.cn/torrents.php?incldead=0&spstate=0&inclbookmarked=0&picktype=0&search=[keyword]&search_area=0&search_mode=0'
    #keyword=input('搜索关键字：\n')
    requrl=baseurl.replace('[keyword]',urllib.parse.quote(keyword))
    return requrl

def HttpGet(url,auto_retry=False,max_retry=3):
    while(max_retry):
        max_retry=max_retry-1
        req=urllib.request.Request(url)
        if not cookie:
            print('请设置cookie值')
            return 'no cookie'
        else:
            req.add_header('Cookie',cookie)
        if not useragent:
            print('推荐设置User-Agent')
        else:
            req.add_header('User-Agent',useragent)
        try:
            response=urllib.request.urlopen(req)
        except:
            print('访问过于频繁,15秒后重试')
            time.sleep(5)
            print('还剩10s')
            time.sleep(5)
            print('还剩5s')
            time.sleep(5)
            print('重试')
            while(not auto_retry):
                confirm=input('是否重试？（y/n）')
                if confirm=='y' or confirm =='Y':
                    break
                elif confirm=='n' or confirm=='N':
                    return 'HTTPerror'
                else:
                    print('illegal input')
            continue
        text=response.read()
        return text     #bytes not utf-8, should decoded later when used
    #texthtml=response.read().decode('UTF-8')

def ShowResult(texthtml):
    pattern='<a title=\".{1,} href=".{1,}"><b>.{1,}</b></a>.{0,}?</td>'
    out=re.findall(pattern,texthtml)
    count=0
    detail=[]
    print('结果如下：')
    for message in out:
        if len(message)>30:
            #print(message)
            title=re.search('title=\".{1,} href',message)
            subtitle=re.search('<br />.{0,}?</td>',message)
            link=re.search('href=\".{1,}?\"',message)
            if subtitle:
                small=[title.group()[7:-8],subtitle.group()[6:-6],'https://pt.sjtu.edu.cn/'+link.group()[6:-1]]
            else:
                small=[title.group()[7:-8],'-','https://pt.sjtu.edu.cn/'+link.group()[6:-1]]
            detail.append(small)
            print(str(count+1)+'. '+detail[count][0]+'\n      '+detail[count][1]+'\n    链接：'+detail[count][2]+'\n')
            count=count+1
    if count==0:
        print('\t没有结果')
        return -1
    else:
        return detail

def DownloadTorrent(num,detail,path='downloads'):
    #num=input('下载哪个？（1~%s，输入0取消下载）'%count)
    num=int(num)
    print(str(num)+'. '+detail[num-1][0]+'\n      '+detail[num-1][1]+'\n    链接：'+detail[num-1][2])
    this_url=detail[num-1][2]
    pagetext=HttpGet(this_url,True)
    pagetext=pagetext.decode('utf-8')
    downloadlink=re.search('下载种子.{0,}?\">',pagetext)
    if downloadlink:
        downid=re.search('=\".{0,}?\"',downloadlink.group())
        finallink='https://pt.sjtu.edu.cn/'+downid.group()[2:-1]
        #print(finallink)
    else:
        print('No download link')
        return -1

    name=detail[num-1][0]
    filematch=re.search('\[.{0,}\]',name)

    #if filematch:
        #filename='[PT]'+filematch.group().replace(' ','_')+'.torrent'
        #print(filename)
    # else:
    #     print('error, no filename')
    #     return -1
    filename='[PT]'+name+'.torrent'
    down_dir=os.path.join(path,filename)
    #print(down_dir)
    #urllib.request.urlretrieve(finallink,down_dir)
    # while(1):
    #     confirm=input('确认下载？（y/n）')
    #     if confirm=='n' or confirm=='N':
    #         print('取消下载')
    #         exit()
    #     elif confirm=='y' or confirm=='Y':
    downtext=HttpGet(finallink,True)
    downfile=open(down_dir,'wb')
    #downtext=downres.read()#.decode('utf-8')
    downfile.write(downtext)
    downfile.close()
    print('下载成功，路径：%s' % down_dir)
    return down_dir
    #     exit()
    # else:
    #     print('请输入正确的字母（y/n）')

def main():
    keyword=input('搜索关键字：')
    url=GetSearchUrl(keyword)
    html=HttpGet(url,False)
    if html=='no cookie':
        exit()
    elif html=='HTTPerror':
        exit()
    html=html.decode('utf-8')
    detail=ShowResult(html)
    if detail==-1:
        exit()
    while(1):
        num=input('下载哪个？（1~%d，0：放弃下载，a：全部下载）'% len(detail))
        if num=='a':
            path=input('设置路径：如downloads/pack，或D:\mytorrent\n')
            for i in range(len(detail)):
                if i:
                    time.sleep(5)
                DownloadTorrent(i+1,detail,path)
        elif int(num)==0:
            exit()
        elif int(num)>0 and int(num)<=len(detail):
            DownloadTorrent(num,detail)
        else:
            print('illegal input')

main()
