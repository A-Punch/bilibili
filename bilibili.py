




import re
from bs4 import BeautifulSoup
from selenium import webdriver
import sqlite3
import requests
import json

def main():

    # baseurl = "https://space.bilibili.com/"
    api_url1 = "https://api.bilibili.com/x/space/acc/info?mid="
    api_url2 = "https://api.bilibili.com/x/relation/stat?vmid="
    begin_i = eval(input("开始uid："))
    end_i = eval(input("结束uid："))+1
    init_sqlite_api("bilibili_api_info.db")
    getData_api(api_url1,api_url2,begin_i,end_i)

    # for i in range(1, 11):
    #     url = baseurl + str(i)
    #     html = Url(url)
    #     datalist = getData(html)
    #     if datalist==[]:
    #         url = baseurl + str(i)
    #         html = Url(url)
    #         datalist = getData(html)
    #     else:
    #         sqname = "bilibili_user_info.db"
    #         saveSqlite(datalist,sqname)
    #         print(f"执行{n}次。")
    #         n+=1

findname = re.compile(r'<span id="h-name">(.*?)</span>',re.S)   #昵称

findlvl = re.compile(r'<a class="h-level m-level" href="//www.bilibili.com/html/help.html#k" lvl="(\d)" target="_blank"')  #等级

findvip = re.compile(r'<a class="h-vipType" href="//account.bilibili.com/account/big" target="_blank">(.*?)</a>') #会员

findsubmit = re.compile(r'<span class="n-text">投稿</span><span class="n-num">(.*?)</span>',re.S)  #投稿数量

findchannel = re.compile(r'<span class="n-text">频道</span><span class="n-num">(.*?)</span>',re.S)   #频道数量

findfownum = re.compile(r'<p class="n-data-v space-attention" id="n-gz">(.*?)</p>',re.S)  #关注数

findfannum = re.compile(r'<p class="n-data-v space-fans" id="n-fs">(.*?)</p>',re.S)  #粉丝数

findheadimg = re.compile(r'<img id="h-avatar" src="(.*?)"/>',re.S)  #头像链接


def getData(html):
    datalist = []   #690313123


    soup = BeautifulSoup(html,"html.parser")
    print('doing getData')
    for item in soup.find_all('div',class_="visitor"):
        data = []
        item = str(item)

        name = re.findall(findname,item)[0]
        # print(name)
        data.append(name)

        templvl = re.findall(findlvl,item)[0]
        lvl = "LV"+str(templvl)
        data.append(lvl)

        try:
            vip = re.findall(findvip,item)[0]
            data.append(vip)
        except:
            data.append("无会员")

        submit = re.findall(findsubmit,item)[0]
        data.append(submit.strip())

        channel = re.findall(findchannel,item)[0]
        data.append(channel.strip())

        fownum = re.findall(findfownum,item)[0]
        data.append(fownum.strip())

        fannum = re.findall(findfannum,item)[0]
        data.append(fannum.strip())

        headimg = re.findall(findheadimg,item)[0]
        request = requests.get("http:"+headimg)
        img =request.content
        path = saveimg(name,img)
        data.append(path)

        datalist.append(data)
        # print(datalist)
        print('getData end')
    return datalist

def getData_api(api1,api2,begin_i,end_i):
    apiUrl1 = api1
    apiUrl2 = api2

    for i in range(begin_i,end_i):
        try:
            datalist = []
            url1 = apiUrl1+str(i)+"&jsonp=jsonp"
            url2 = apiUrl2+str(i)+"&jsonp=jsonp"

            api_json1 = apiurl(url1)
            api_json2 = apiurl(url2)


            UID = api_json1['data']['mid']
            datalist.append(UID)

            name = api_json1['data']['name']
            datalist.append(name)

            sex = api_json1['data']['sex']
            datalist.append(sex)

            level = api_json1['data']['level']
            datalist.append(level)

            if(api_json1['data']['fans_badge']==False):
                fans_badge = "未开通"
                datalist.append(fans_badge)
            elif(api_json1['data']['fans_badge']==True):
                fans_badge = "已开通"
                datalist.append(fans_badge)

            vip = api_json1['data']['vip']['label']['text']
            if vip=="":
                vip = "无大会员"
            datalist.append(vip)

            following = api_json2['data']['following']
            datalist.append(following)

            follower = api_json2['data']['follower']
            datalist.append(follower)

            face_img = api_json1['data']['face']
            img = requests.get(face_img).content
            path = saveimg(name,img)
            datalist.append(path)

            # print(datalist)
            try:
                saveSqlite_api(datalist,"bilibili_api_info.db")
            except:
                pass
        except:
            pass




def apiurl(apiurl):
    headers = {
        "user-agent": "Mozilla / 5.0(Windows NT 10.0;WOW64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 78.0.3904.108Safari / 537.36"
    }
    url = apiurl

    response = requests.get(url,params=None,headers = headers).json()


    # print(response)
    return response

def Url(url):
    PATH = "F:\python\Scripts\chromedriver.exe"
    Chrome = webdriver.Chrome(executable_path=PATH)
    Chrome.get(url)

    html = Chrome.page_source

    return html

def saveSqlite(datalist,sqname):
    print('doing savesqlite')
    try:
        init_sqlite(sqname)
    except:
        pass
    conn = sqlite3.connect(sqname)
    sql = '''
            insert into BILIBILI_USERS_INFO( 昵称, 等级, 会员, 投稿数量, 频道数, 关注数, 粉丝数, 头像地址)
            values (?,?,?,?,?,?,?,?)
    '''
    cur = conn.cursor()
    for userinfo in datalist:
        cur.execute(sql,userinfo)
        conn.commit()
        print(f"{userinfo[0]}的基本信息已保存到数据库。")

    conn.close()
    print('savesqlite end')

def saveSqlite_api(datalist,sqname):
    try:

        init_sqlite_api(sqname)
    except:

        pass
    conn = sqlite3.connect(sqname)
    sql = '''
            insert into BILIBILI_USERS_INFO_api(UID,昵称,性别,等级,粉丝勋章,会员,关注数,粉丝数,头像地址)
            values (?,?,?,?,?,?,?,?,?)
    '''
    cur = conn.cursor()

    cur.execute(sql,datalist)
    conn.commit()
    print(f"{datalist[1]}的信息已保存到数据库。")
    conn.close()

def update_sqlite(sqname,datalist):
    conn = sqlite3.connect(sqname)
    cur = conn.cursor()
    cur.execute(f"delete from BILIBILI_USERS_INFO_api where UID= {datalist[0]} ")
    conn.commit()
    conn.close()
    saveSqlite_api(datalist, sqname)

def init_sqlite_api(sqname):
    try:
        sql = '''
                create table BILIBILI_USERS_INFO_api(
                UID integer primary key not null,
                昵称 varchar not null,
                性别 varchar not null,
                等级 varchar not null,
                粉丝勋章 varchar not null,
                会员 varchar not null,
                关注数 integer not null,
                粉丝数 integer not null,
                头像地址 text not null
                )
        '''
        conn = sqlite3.connect(sqname)
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        conn.close()
    except:
        pass


def init_sqlite(sqname):
    sql = '''
           
            create table BILIBILI_USERS_INFO(
            UID integer primary key,
            昵称 varchar not null,
            等级 integer not null,
            会员 integer not null,
            投稿数量 integer not null,
            频道数 integer not null,
            关注数 integer not null,
            粉丝数 integer not null,
            头像地址 text
            )
    '''
    conn = sqlite3.connect(sqname)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    conn.close()

def saveimg(name,img):
    try:
        path = './bilibili_HDIMG/'+name+'.gif'
        with open(path,'wb') as f:
            f.write(img)
        print(f"{name}的头像保存成功。")
    except:
        print(f"{name}的头像保存失败。")
        pass
    return path


if __name__ == "__main__":
    main()