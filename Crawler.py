import requests
import re
from utility import *

# maybe these urls should store in a json file
root = "http://zhjw.scu.edu.cn/"
root_stu = root + "student/"
login_url = root + "j_spring_security_check"
captcha_url = root + "img/captcha.jpg"
class_course_table = root_stu + "teachingResources/classCurriculum/searchCurriculumInfo/callback"
student_course_url = root_stu + "courseSelect/thisSemesterCurriculum/ajaxStudentSchedule/past/callback"
scores_url = root_stu + "integratedQuery/scoreQuery/schemeScores/callback"
courses_search_url = root_stu + "integratedQuery/course/courseBasicInformation/show"
exam_plan_url = root_stu + "examinationManagement/examPlan/index"  # all info is in the response
course_query_url = root_stu +  "courseSelect/freeCourse/courseList" # POST

# courses select region

course_select_query = root_stu + "courseSelect/selectResult/query"

# courses select endregion

filepath = ".local/"
class_info = filepath + "class.json"
payload = filepath + "payload.json"
header = filepath + "header.json"
course_query_payload={
    "searchtj": "", # 搜索内容
    "xq": 0, # 星期 0代表所有
    "jc": 0, # 节次
    "kclbdm": None # 课程类别
    # 空为全部

}

def calc_default_term(start_year: int) -> int:
    """
    :param start_year: the year you recruit
    :return: the seq of current semester
    """
    import datetime
    year = datetime.datetime.today().year
    # 2021-10 -> 5 2019-10 -> 1
    up_of_stu_year = 1 if datetime.datetime.today().month > 8 else 0
    return (year - start_year) * 2 + up_of_stu_year


class CoursesCrawl:
    def __init__(self):
        self.session = requests.session()  # create a session
        self.header = {}
        self.payload = {}
        self.class_id = self.read_class()
        self.login_flag = False

    def get_session(self) -> requests.sessions:
        return self.session

    def read_class(self, class_file: str = class_info):
        try:
            with open(class_info, encoding="utf8") as cid:
                return json.loads(cid.read())["classId"]
        except IOError:
            return None

    def read_header(self, header_file: str = header):
        with open(header_file, encoding="utf8") as conf:  # read header
            self.header = json.loads(conf.read())

    def crawl_table(self, verbose: bool = False):
        # 通过配置文件读取 header 账号和密码
        self.read_header()
        self.read_payload()
        # 登录
        succ, msg = self.login()
        if not succ:
            print(msg)
            return
        else:  # 获取课表并保存
            if not self.search_table(verbose=verbose):
                print("拉取课表错误")

    def crawl_exam_list(self):
        self.read_header()
        self.read_payload()
        # 登录
        succ, msg = self.login()
        if not succ:
            print(msg)
            return
        else:  # 获取课表并保存
            if not self.get_exam():
                print("拉取考表错误")

    def get_exam(self, save: bool = False, url: str = exam_plan_url,
                 base_file_name: str = filepath + "exam") -> bool:
        response = self.session.get(url, headers=self.header)
        if response.status_code != 200:
            return False
        html = response.text.replace("\n", "").replace("\t", "").replace("\r", "")
        msg = Utility.norm_exam(html, save, is_file=False, savefile=base_file_name)
        return True

    def search_table(self, save: bool = True, *, baseurl: str = class_course_table,
                     term: str = "2021-2022-2-1", classId: str = "193040111",
                     verbose=False):
        url = f"{baseurl}?planCode={term}&classCode={classId}"
        #     if verbose:print(data)
        response = self.session.get(url, headers=self.header)
        response.encoding = "utf8"
        if response.status_code != 200:
            if verbose:
                print(response.text)
            return False
        useful_info = json.loads(response.text)[0]
        Utility.norm_class(useful_info, save, is_file=False)
        with open(class_info, "w", encoding='utf8') as cinfo:
            cinfo.write(f'{{"classId":{classId}}}')
        if save:
            with open(filepath + "table.json", "w", encoding='utf8') as course_fd:
                course_fd.write(json.dumps(useful_info, ensure_ascii=False))
        return True

    def read_payload(self, data: str = payload, *, verbose: bool = False):
        with open(data, encoding="utf8") as conf:  # read payload
            self.payload = json.loads(conf.read())
            # 获取 captcha 并通过ocr识别
            j_captcha = self.get_captcha(captcha_url, verbose)
            self.payload["j_captcha"] = j_captcha  # 添加验证码字段

    def login(self, url: str = login_url):
        if self.login_flag:
            return True, ""
        response = self.session.post(url, data=self.payload, headers=self.header)
        # validate if logins
        pattern = "<strong>发生错误!</strong>(.*?)\\s*</div>"
        succ = response.text.find("<title>登录</title>") == -1
        error_msg = None if succ else re.findall(pattern, response.text)[0]
        if succ: self.login_flag = True
        return succ, error_msg

    def is_logged(self) -> bool:
        return self.login_flag

    def get_captcha(self, url: str = captcha_url, process: bool = False):
        captcha = self.session.get(url).content  # get image
        rel = ocr(captcha, True)
        if process:
            with open(filepath + "tmp.png", "wb") as fd:
                fd.write(captcha)
            import matplotlib.pyplot as plt
            from PIL import Image
            img = Image.open(filepath + "tmp.png")
            plt.imshow(img)
            print(rel)
        return rel  # ocr process

    @staticmethod
    def calc_plan_code(year: int, term: int = None) -> str:
        # 2019 1 -> 2019-2020-1-1
        # 2019 6 -> 2021-2022-2-1
        term = calc_default_term(year) if term is None else term
        term -= 1
        yd = term // 2
        term = term % 2 + 1
        return f"{year + yd}-{year + yd + 1}-{term}-1"

    @staticmethod
    def save_head(sid: str, md5_pass: str, datafile=payload):
        pay = {
            "j_username": sid,
            "j_password": md5_pass,
        }
        # print(header)
        with open(datafile, 'w', encoding="utf8") as conf:
            conf.write(json.dumps(pay))
