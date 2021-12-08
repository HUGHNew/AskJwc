from Interpreter import *
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="fetch your relative data in SCU URP")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-d", "--direct", help="get the course table directly and write to class.csv file",
                       action="store_true")
    group.add_argument("-e", "--exam", help="get the exam directly and write to exam.csv file", action="store_true")
    args = parser.parse_args()
    it = Interpreter()
    if args.direct:
        if it.login():
            it.table()
    elif args.exam:
        if it.login():
            it.table()
    else:
        it.run()
