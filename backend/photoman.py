import logging
import sys
import utilities.rename

def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)


def main():
    setup_logging()
    logging.info("Hello")
    utilities.rename.rename_files("aaa")



if __name__ == '__main__':
    main()
