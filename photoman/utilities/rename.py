import logging
import sys
import exifread # type: ignore
from datetime import datetime
import pathlib
import os
import shutil
import filecmp
import subprocess
from typing import Optional, Tuple, List

exifread.logger.disabled = True
date_str_default = "1970:01:01 00:00:00"


class FileIsADuplicate(Exception):
    pass


class FFMpegNotFound(Exception):
    pass


class InvalidDateFormat(Exception):
    pass


def parse_date_str(date_str: str) -> datetime:
    date_formats = ["%Y:%m:%d %H:%M:%S", "%d/%m/%Y %H:%M",
                    "%Y-%m-%d %H:%M:%S ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ"]
    date = None
    for date_format in date_formats:
        try:
            date = datetime.strptime(date_str, date_format)
            break
        except ValueError:
            continue
    if date is None:
        raise InvalidDateFormat
    return date


def get_date_str(filename: str, use_short_name: bool)-> Tuple[str, str]:
    if(filename.upper().endswith(".JPG") or filename.upper().endswith(".CR2")):
        ret = get_date_str_image(filename, use_short_name)
    elif(filename.upper().endswith(".AVI")
            or filename.upper().endswith(".MP4")
            or filename.upper().endswith(".MOV")
            or filename.upper().endswith(".3GP")
            or filename.upper().endswith(".M4V")
            or filename.upper().endswith(".MPG")):
        ret = get_date_str_video(filename)
    elif(filename.upper().endswith(".RW2")):
        ret = get_date_str_rw2(filename)
    return ret


def get_date_str_video(filename: str) -> Tuple[str,str]:
    try:
        ffprobe_out = subprocess.run(
            ["ffprobe", filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:  # pragma: no cover
        raise FFMpegNotFound

    try:
        ffprobe_str = ffprobe_out.stdout.decode(
            "utf-8") + "\n" + ffprobe_out.stderr.decode("utf-8")
        ffprobe_lines = ffprobe_str.split("\n")
        dates = []
        for line in ffprobe_lines:
            if "creation_time" in line:
                dates.append(":".join(line.split(":")[1:]).strip())

        date_str = dates[0]
    except:
        date_str = date_str_default

    date = parse_date_str(date_str)
    return (date.strftime("%Y%m%d_%H%M%S"), date.strftime("%Y-%m-%d") + "-video")


def get_date_str_image(filename: str, use_short_name: bool) -> Tuple[str, str]:
    f = open(filename, "rb")
    tags = exifread.process_file(f)
    try:
        date_str = str(tags["EXIF DateTimeOriginal"])
    except KeyError:
        date_str = date_str_default

    try:
        model_name = str(tags["Image Model"])
    except KeyError:
        model_name = "UNKNOWN"
    model_name = model_name.replace(" ", "_")
    model_name = model_name.replace("<", "")
    model_name = model_name.replace(">", "")
    model_name = model_name.replace("\\", "")
    model_name = model_name.replace("/", "")

    date = parse_date_str(date_str)

    if use_short_name:
        ret = (date.strftime("%Y%m%d_%H%M%S"), date.strftime("%Y-%m-%d"))
    else:
        ret = (date.strftime("%Y%m%d_%H%M%S"), date.strftime("%Y-%m-%d") + "-" + model_name)

    return ret

def get_date_str_rw2(filename: str) -> Tuple[str, str]:
    data: str = ""

    with open(filename, 'rb') as f:
        f.seek(0x0E46)
        data = f.read(19).decode('utf-8')

    date = parse_date_str(data)

    return (date.strftime("%Y%m%d_%H%M%S"), date.strftime("%Y-%m-%d"))



def move_file(oldname: str, newname: str, create_dirs: bool) -> None:
    os.makedirs(os.path.dirname(newname), exist_ok=True)

    logging.debug("Will move file {0} to {1}".format(oldname, newname))

    if not os.path.exists(newname):
        try:
            os.rename(oldname, newname)
        except OSError:  # pragma: no cover
            shutil.move(oldname, newname)
    else:
        if not (oldname == newname):
            files_identical = filecmp.cmp(oldname, newname, shallow=False)
            if files_identical:
                logging.warning("File {} is a duplicate.".format(oldname))
                raise FileIsADuplicate()
            else:
                raise FileExistsError()


def rename_files(filenames: List[str], output_dir: str, create_dirs:bool=False, remove_duplicates:bool=False, short_dir_names:bool=False) -> None:
    num_total = len(filenames)
    num_current = 0
    for file_path in filenames:
        try:
            original_file_path_str = file_path
            (date_str, dir_str) = get_date_str(original_file_path_str, short_dir_names)
            new_file_path_str = output_dir

            original_file_path = pathlib.PurePath(file_path)
            original_filename = original_file_path.name
            extension = str(original_file_path.suffix)
            original_filename = original_filename.replace(extension, '')

            name_suffix_n = 0
            while True:
                date_str_to_write = ""
                if create_dirs:
                    date_str_to_write = str(os.path.join(dir_str, date_str))
                else:
                    date_str_to_write = date_str
                if name_suffix_n > 0:
                    date_str_to_write = date_str_to_write + \
                        "_" + str(name_suffix_n)

                new_file_path_str = output_dir + date_str_to_write + extension.upper()
                try:
                    move_file(original_file_path_str,
                              new_file_path_str, create_dirs)
                    logging.info("{:3.0f}".format(num_current*100/num_total) + "%\t" +
                                 str(original_file_path_str) + "\t-->\t" + new_file_path_str)
                except FileExistsError:
                    name_suffix_n += 1
                    continue
                except FileIsADuplicate:
                    if remove_duplicates:
                        logging.error("deleting {} ...".format(
                            original_file_path_str))
                        os.remove(original_file_path_str)
                break
        except KeyboardInterrupt:  # pragma: no cover
            raise
        except FFMpegNotFound as e:  # pragma: no cover
            raise e
        except:  # pragma: no cover
            logging.warning("{:3.0f}".format(
                num_current*100/num_total) + "%\t" + str(file_path) + "\t-->\t <skipping>")
            logging.exception("ERROR")
        num_current = num_current + 1
