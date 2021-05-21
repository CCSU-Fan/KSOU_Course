import requests,re,time,math,random,json
from bs4 import BeautifulSoup
from requests.api import post

def Get_PostData(LoginUrl):
    '''
       获取登录参数
    '''
    Req_Class = requests.get(LoginUrl)#获取Get对象,准备那曲第一次Cookie
    Req_Cookies = Req_Class.cookies["JSESSIONID"]#获取请求Cookie
    Html_Text = Req_Class.text#获取源码
    Soup_Class = BeautifulSoup(Html_Text,"lxml")#转为Soup对象
    Tag_NameT = ('input[name="lt"]','input[name="execution"]','input[name="_eventId"]','input[name="rmShown"]')#标签元组
    Data_ValueL = []#值列表
    for Value in Tag_NameT:
        Data_V = Soup_Class.select(Value)[0]#获取TAG对象
        Regex_Class = re.compile(r'(?<=value=\").+(?=\"\/\>)')#编译正则表达式
        Data_ValueL.append(Regex_Class.findall(str(Data_V))[0])#获取参数加入列表
    return Data_ValueL,Req_Cookies

def Start_Login():
    '''
    开始登录
    
    '''
    ValueData,Req_Cookie = Get_PostData(LoginUrl)
    Post_data = {
        "username":213208130117912,#用户名
        "password":123456,#密码
        "lt":ValueData[0],
        "execution":ValueData[1],
        "_eventId":ValueData[2],
        "rmShown":int(ValueData[3])
        }#构造发包数据
    Post_Headers = {"Host":"ids3.jsou.cn","cookie":"JSESSIONID="+Req_Cookie}#构造headers
    Post_Rep = requests.post(LoginUrl,data=Post_data,headers=Post_Headers,allow_redirects=False)#发包并且禁止重定向
    Redirect_Url = Post_Rep.headers["Location"]#获取重定向url
    Redirect_Req = requests.get(Redirect_Url,allow_redirects=False)#进行重定向url访问拿到登录成功的cookie
    Login_Cookie = Redirect_Req.headers["Set-Cookie"].split(';')[0]#分割取首
    return Login_Cookie

def Get_CourseId(CourseUrl,LoginHeaders):#获取课程总ID
    Raw_Json_Data = requests.post(CourseUrl,headers=LoginHeaders).json()
    Course_D = {}
    Course_IDL = []
    for Each_Course_Info in Raw_Json_Data['body']:
        Course_Id = Each_Course_Info["courseVersionId"]
        Course_Name = Each_Course_Info["courseName"]
        Course_D[Course_Id] = Course_Name
        Course_IDL.append(Course_Id)
    return Course_D,Course_IDL
    
def Get_Course_ContentUrl(): #获取各个课程API URL
    Course_ID,CourseID_NameD = Get_CourseId(CourseUrl,LoginHeaders)
    Content_Urls = []
    for ID in Course_ID:
        Course_ContentUrl = "http://xuexi.jsou.cn/jxpt-web/student/course/getAllActivity/"+ID
        Content_Urls.append(Course_ContentUrl)
    return Content_Urls

def Get_Course_VideoDetail():#获取各个课程下属全部视频信息
    Content_Urls = Get_Course_ContentUrl()
    Active_IDS = []#存放CourseID
    Deal_U = []#存放ActiveID
    for Url in Content_Urls:#进行第一层循环
        Course_DeatilContent = requests.get(Url,headers=LoginHeaders).json()['body']
        Course_Json_Len = len(Course_DeatilContent)
        for Index in range(0,Course_Json_Len):#进行第二层循环
            Avtive_List = Course_DeatilContent[Index]["activitys"]
            for Active_Info in Avtive_List:#进行第三层循环
                Type_Ac = Active_Info["type"]
                if(Type_Ac == "2"):#过滤非视频链接
                    ACtiveID_CourseID = {}
                    Deal_Url = Url.replace("http://xuexi.jsou.cn/jxpt-web/student/course/getAllActivity/","")#处理课程URL，提取CRL
                    Active_IDS.append(Active_Info["activityId"])#存储AID
                    Deal_U.append(Deal_Url)#存储CID
    return Deal_U,Active_IDS

def SetToken():#根据网站逆向得出Token算法
    len_ = 8.or(32)
    Salt = "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678"
    MaxPos = len(Salt)
    Pwd = ""
    i = 0
    while(i<len_):
        i+=1
        Pwd+=Salt[math.floor(random.random()*MaxPos)]
    return Pwd
    
def Make_Heart():#制作心跳包
    HeartVer_Url = "http://xuexi.jsou.cn/jxpt-web/common/learningBehavior/heartbeat"
    C_Url,A_Url = Get_Course_VideoDetail()
    Post_Data0 = {
        "playStatus":"true",
        "isResourcePage":"true",
        "courseVersionId":"0",
        "activityId":"0",
        "type":2,
        "isStuLearningRecord":2,
        "token":SetToken(),#生成token
        "timePoint":random.random()*100
    }
    Post_Data1 = {}
    Post_Data2 = {}
    Heart_PostPackages = []
    for CID in C_Url:
        Post_Data0["courseVersionId"]=CID#进行cid更新
        Post_Data1.update(Post_Data0)#存储更新后的心跳包
    for AID in A_Url:
        Post_Data1["activityId"] = AID#进行aid更新
        Post_Data2.update(Post_Data1)#存储aid更新心跳包
        Heart_PostPackages.append(Post_Data2)
    return Heart_PostPackages#返回所有视频心跳构造包

def Start_Run():
    Post_D = Make_Heart()
    Count = 0
    for P_E in Post_D:
        Count+=1
        Repo = requests.post(HeartBeatUrl,headers=LoginHeaders,data=P_E,timeout=3).json()
        if(Repo["error"]==False):
            print("刷课运行正常，正在进行第{}个视频".format(Count))
    Count=0

    
if __name__ == "__main__":

    Num = 0
    LoginUrl = "https://ids3.jsou.cn/login?service=http://xuexi.jsou.cn/jxpt-web/auth/idsLogin"
    CourseUrl = "http://xuexi.jsou.cn/jxpt-web/student/courseuser/getAllCurrentCourseByStudent"
    HeartBeatUrl = "http://xuexi.jsou.cn/jxpt-web/common/learningBehavior/heartbeat"
    LoginHeaders = {"Host":"xuexi.jsou.cn","Cookie":Start_Login()}
    while True:
        Start_Run()
        Num+=1
        print("\n第{}轮结束,第{}轮即将开始...\n".format(Num,Num+1))
    
    

