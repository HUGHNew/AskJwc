import hashlib
import json
import ddddocr
from enum import Enum


class CrawlType(Enum):
    Class_Schedule = "class"
    Student_Schedule = "student"
    Score = "score"
    Course_Info = "info"
    Exam_Plan = "exam"

# csv first column
norm_class_header = "课程名,课序号,教师名,上课周数,上课节数,上课地点"
exam_csv_headers = "课程名,考试日期,考试时间,考试地点,座位号"
filepath = ".local/"


def ocr(file, direct: bool = False, *, limit: int = 4) -> str:
    if not direct:
        with open(file, 'rb') as f:
            img_bytes = f.read()
    else:
        img_bytes = file
    rel = ddddocr.DdddOcr().classification(img_bytes)
    if len(rel) > limit:
        return rel[-limit:]
    return rel


def md5(data: str):
    return hashlib.md5(data.encode(encoding='UTF-8')).hexdigest()


def md5_interact(prompt: str):
    return md5(input(prompt))

# normalize the info to csv format that the crawler fetched
class Utility:
    @staticmethod
    def normalize_create(info_type: CrawlType):
        return getattr(Utility, "norm_" + info_type.name)

    @staticmethod
    def norm_base(filename: str):
        with open(filename) as fd:
            return json.loads(fd.read())

    @staticmethod
    def norm_class_str(course) -> str:
        c = course
        d = c["id"]
        course_times = str(d["skjc"]) + "~" + str(d["skjc"] + c["cxjc"])
        return ",".join(list(map(lambda x: x.replace(",", " "),
                                 [c["kcm"], d["kxh"], c["jsm"], c["zcsm"],
                                  course_times, c["jxlm"] + c["jxlh"]])))

    @staticmethod
    def norm_class(file: str, save: bool = False, *, is_file: bool = True,
                   save_file_base: str = filepath + "table"):
        content = Utility.norm_base(file) if is_file else file
        # save as csv
        head = norm_class_header + "\n"
        body = "\n".join([course for course
                          in map(lambda c: Utility.norm_class_str(c), content)])
        msg = head + body
        if save:
            with open(save_file_base + ".csv", "w", encoding='utf8') as fd:
                fd.write(msg)
        else:
            print(msg)
        return msg

    @staticmethod
    def norm_student(file: str, save: bool = False, *, is_file: bool = True):
        content = Utility.norm_base(file) if is_file else file
        pass  # todo

    @staticmethod
    def norm_score(file: str, save: bool = False, *, is_file: bool = True):
        content = Utility.norm_base(file) if is_file else file
        pass  # todo

    @staticmethod
    def norm_exam(file: str, save: bool = False, *,
                  is_file: bool = True, savefile=filepath + "exam.csv"):
        """
        normalization exam info
        """
        html = Utility.norm_base(file) if is_file else file
        course_list_pat = '<div class="widget-box widget-color-blue">(.*)</div>'  # phase one
        course_pat = '<h5 class="widget-title smaller">(.*?)</h5>.*?<div class="widget-main">(.*?)</div>'  # phase two
        # tuples [0] -- name [1] -- info
        # get exam items by regex
        all_exam_courses = re.findall(course_pat, re.findall(course_list_pat, html)[0])


        def get_exam_item(it):
            name = it[0].split("）", 1)[1]
            rel = it[1].split("&nbsp;")
            # print(it)
            get = lambda x: x.split("</br>")[0]
            return [name, rel[3], get(rel[5]), get(rel[7]) + get(rel[8]), get(rel[9])]

        body = [",".join(get_exam_item(item)) for item in all_exam_courses]
        msg = "\n".join([exam_csv_headers, *body])
        if save:
            with open(savefile, encoding="utf8") as exam:
                exam.write(msg)
        else:
            print(msg)
        return msg
