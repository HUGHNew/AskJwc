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


norm_class_header = "课程名,课序号,教师名,上课周数,上课节数,上课地点"
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
        if save:
            with open(save_file_base + ".csv", "w", encoding='utf8') as fd:
                fd.write(head + body)
        else:
            print(head + body)
        pass  # todo

    @staticmethod
    def norm_student(file: str, save: bool = False, *, is_file: bool = True):
        content = Utility.norm_base(file) if is_file else file
        pass  # todo

    @staticmethod
    def norm_score(file: str, save: bool = False, *, is_file: bool = True):
        content = Utility.norm_base(file) if is_file else file
        pass  # todo

    @staticmethod
    def norm_info(file: str, save: bool = False, *, is_file: bool = True):
        content = Utility.norm_base(file) if is_file else file
        pass  # todo
