import logging
import sys
import exifread
from datetime import datetime
import pathlib
import os


def get_date_str(filename):
    f = open(filename, "rb")
    tags = exifread.process_file(f)
    date_str = str(tags["Image DateTime"])

    date = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
    return date.strftime("%Y%m%d_%H%M%S")


def rename_files(filenames):
    for file_path in filenames:
        try:
            original_file_path = file_path
            date_str = get_date_str(original_file_path)
            original_file_path_str = file_path
            new_file_path_str = original_file_path_str

            original_file_path = pathlib.PurePath(file_path)
            original_filename = original_file_path.name
            extension = str(original_file_path.suffix)
            original_filename = original_filename.replace(extension, '')

            name_suffix_n = 0
            while True:
                date_str_to_write = date_str
                if name_suffix_n > 0:
                    date_str_to_write = date_str + "_" + str(name_suffix_n)
                new_file_path_str = original_file_path_str.replace(original_filename, date_str_to_write)
                try:
                    os.rename(original_file_path_str, new_file_path_str)
                    logging.info(str(file_path) + "\t-->\t" + new_file_path_str)
                except:
                    name_suffix_n += 1
                    continue
                break
        except:
            logging.warning(str(file_path) + "\t-->\t <skipping>")


if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(message)s")
    ch.setFormatter(formatter)
    root.addHandler(ch)

    exifread.logger.disabled = True

    rename_files(sys.argv[1:])
