import argparse
import logging
import sys
import os
from typing import List


def setup_logging(verbose: bool = True) -> None:
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    if(verbose):
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)


def format_extensions(extensions: List[str]) -> List[str]:
    full_extensions = []
    for extension in extensions:
        full_extensions.append(extension.upper())
        full_extensions.append(extension.lower())
    return full_extensions


def filter_by_extension(input: List[str], extensions: List[str]) -> List[str]:
    output = []
    for filename in input:
        if filename.endswith(tuple(extensions)):
            output.append(os.path.realpath(filename))
    return output


def get_file_list(start_dir: str, extensions: List[str], recursive: bool = False) -> List[str]:
    full_dir = os.path.realpath(start_dir)
    full_extensions = format_extensions(extensions)
    logging.debug("Getting file list:")
    logging.debug("\troot directory: {0}".format(full_dir))
    logging.debug("\tsearching extensions: {0}".format(
        " ".join(full_extensions)))
    logging.debug("\trecursive: {0}".format(recursive))

    all_candidates = []

    if recursive:
        for root, dirs, files in os.walk(full_dir):
            for name in files:
                all_candidates.append(os.path.join(root, name))
            for name in dirs:
                all_candidates.append(os.path.join(root, name))
    else:
        candinates = os.listdir(full_dir)
        for candidate in candinates:
            all_candidates.append(os.path.join(full_dir, candidate))

    files = filter_by_extension(all_candidates, full_extensions)
    logging.debug("\tFound files:\n\t\t{0}".format("\n\t\t".join(files)))
    return files


def main(argv: List[str]) -> None:
    arg_parser = argparse.ArgumentParser(
        description="Rename images so that new name is its date/time taken.")
    arg_parser.prog = "photoman"
    arg_parser.add_argument(
        "-v", "--verbose", action="store_true", help="be verbose")
    arg_parser.add_argument("-C", "--directory", nargs=1, default=".",
                            required=False, help="specify a working directory.", metavar="directory")
    arg_parser.add_argument("-e", "--extensions", action="append", nargs=1, required=False,
                            help="specify file extensions.", metavar="extensions", default=[])
    arg_parser.add_argument("-r", "-R", "--recursive",
                            action="store_true", help="find images recursively")
    arg_parser.add_argument(
        "-o", "--output", help="specify output directory", metavar="directory")
    arg_parser.add_argument("-z", "--create-dirs", action="store_true",
                            help="create separate directiories for each day and camera")
    arg_parser.add_argument("-d", "--remove-duplicates", action="store_true",
                            help="if a file is considered a duplicate, it will be deleted")
    arg_parser.add_argument("-s", "--short", action="store_true",
                            help="use short directory names (date only)")

    args = arg_parser.parse_args(args=argv)

    setup_logging(args.verbose)

    if (len(argv) == 0) or (len(args.extensions) == 0):
        arg_parser.print_help(sys.stderr)
        sys.exit(1)

    extensions_list = []
    for string_list in args.extensions:
        for string in string_list:
            extensions_list.append(string)
    extensions = " ".join(extensions_list).replace(";", " ").replace(",", " ")
    extensions_list_all = extensions.split(" ")
    extensions_list = []
    for extension in extensions_list_all:
        if(len(extension) > 0):
            extensions_list.append(extension)

    if(args.output is None):
        args.output = args.directory[0]
    files = get_file_list(
        args.directory[0], extensions_list, recursive=args.recursive)

    output_path = os.path.join(os.path.realpath(args.output), "")

    import rename  # type: ignore
    try:
        rename.rename_files(
            files, output_path, args.create_dirs, args.remove_duplicates, args.short)
    except rename.FFMpegNotFound:  # pragma: no cover
        logging.error("Could not find ffprobe.")

    return


if __name__ == '__main__':  # pragma: no cover
    main(sys.argv[1:])
