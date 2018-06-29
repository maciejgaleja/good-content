import logging
import sys


def rename_files(filename):
    logging.info("Renaming file: " + str(filename))


if __name__ == '__main__':
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)
    rename_files(sys.argv[1:])