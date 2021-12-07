from crawlMain import *
import os.path

"""
outer command
- [ ] -d, --direct : get the course table directly with the class.json file
- [ ] -e, --exam : get the exam plan

write to file ($cmd.csv) and 
    show in console if in inline command

inline command
- [x] login
- [x] exam
- [x] table [term] [class]
- [ ] search
- [ ] score
- [x] exit
- [x] help
"""


class Interpreter:
    """
    a cli wrapper of academical affairs crawler
    """

    usage = """commands:
    - login : login through account file(payload.json) if exists or input manually
    - exam : get exam plan
    - table : get class course table with specific term and classId
    - search : search course 
    - score : get scores
    - exit : exit Ask JWC
    - help : get help doc
            """

    def __init__(self, *, prompt: str = ">> ", classrc: str = class_info,
                 userc: str = payload, headerc: str = header):
        self.__classrc = classrc
        self.__userc = userc
        self.__headerc = headerc
        self.__spider = CoursesCrawl()
        self.__prompt = prompt
        self.__process = ""  # store current command

    def run(self):
        while self.parse(input(self.__prompt)):
            pass

    def parse(self, command: str) -> bool:
        print(f"command:{command}")
        if command == "": return True
        self.__process = "help" if command == "?" else command
        try:
            getattr(Interpreter, self.__process)(self)
        except AttributeError:  # command not exist
            print(f"command <{command}> not support")
        except RuntimeError as Argument:
            print(Argument)
        except EnvironmentError:
            return False
        return True

    def login(self):
        try:
            if not os.path.exists(self.__headerc):
                print(f"header file <{self.__headerc}> not exists, aborted")
                raise EnvironmentError
            self.__spider.read_header(self.__headerc)
            self.__spider.read_payload(self.__userc)
        except IOError:
            stu_id = input("没有获取到用户信息\n请输入学号:")
            md5_pass = md5(input("请输入密码(带X默认为大写):"))
            CoursesCrawl.save_head(stu_id, md5_pass, self.__userc)
        finally:
            succeed, msg = self.__spider.login()
            print("成功登录" if succeed else msg)

    def exam(self):
        if self.__spider.get_exam(True):
            with open(filepath + "exam.csv",encoding="utf8") as exam:
                print(exam.readlines())
        else:
            print("获取考表错误")

    def table(self, term: int = None, class_id: str = None):
        year = int(self.__spider.payload["j_username"][:4])
        if not term:
            term = calc_default_term(year)
        plan_code = CoursesCrawl.calc_plan_code(year, term)
        if not class_id:
            if os.path.exists(class_info):
                class_id = self.__spider.class_id
            else:
                class_id = input("请输入查询的班级号")
        code = self.__spider.search_table(term=plan_code, classId=class_id)
        if code:
            with open(filepath + "table.csv", encoding="utf8") as table:
                print(table.readlines())

    def search(self):
        pass

    def score(self):
        pass

    def help(self):
        print(Interpreter.usage)

    def exit(self):
        print("退出 Ask JWC。没事了，再见了您勒")
        raise EnvironmentError


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    Interpreter().run()
