import logging
import sys
import exifread
from datetime import datetime
import pathlib
import os

exifread.logger.disabled = True

def get_date_str(filename):
    f = open(filename, "rb")
    tags = exifread.process_file(f)
    date_str = str(tags["EXIF DateTimeOriginal"])

    model_name = str(tags["Image Model"]).replace(" ", "_")

    date = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
    return (date.strftime("%Y%m%d_%H%M%S"), date.strftime("%Y-%m-%d") + "-" + model_name)


def rename_files(filenames, create_dirs=False):
    num_total = len(filenames)
    num_current = 0
    for file_path in filenames:
        try:
            original_file_path = file_path
            (date_str, dir_str) = get_date_str(original_file_path)
            original_file_path_str = file_path
            new_file_path_str = original_file_path_str

            original_file_path = pathlib.PurePath(file_path)
            original_filename = original_file_path.name
            extension = str(original_file_path.suffix)
            original_file_path_str = original_file_path_str.replace(extension, extension.upper())
            original_filename = original_filename.replace(extension, '')

            name_suffix_n = 0
            while True:
                date_str_to_write = ""
                if create_dirs:
                    date_str_to_write = str(os.path.join(dir_str, date_str))
                else:
                    date_str_to_write = date_str
                if name_suffix_n > 0:
                    date_str_to_write = date_str_to_write + "_" + str(name_suffix_n)

                new_file_path_str = original_file_path_str.replace(original_filename, date_str_to_write)
                try:
                    if create_dirs:
                        os.makedirs(os.path.dirname(new_file_path_str), exist_ok=True)
                    os.rename(original_file_path_str, new_file_path_str)
                    logging.info("{:3.0f}".format(num_current*100/num_total) + "%\t" + str(file_path) + "\t-->\t" + new_file_path_str)
                except:
                    name_suffix_n += 1
                    continue
                break
        except:
            logging.warning("{:3.0f}".format(num_current*100/num_total) + "%\t" + str(file_path) + "\t-->\t <skipping>")
            logging.exception("ERROR")
        num_current = num_current + 1


if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(message)s")
    ch.setFormatter(formatter)
    root.addHandler(ch)

    if(sys.argv[1] == "--dirs"):
        rename_files(sys.argv[2:], True)
    else:
        rename_files(sys.argv[1:], False)