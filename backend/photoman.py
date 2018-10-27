import logging
import sys
import utilities.rename
import os
import argparse

def setup_logging(verbose=True):
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    if(verbose):
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)


def format_extensions(extensions):
    full_extensions = []
    for extension in extensions:
        full_extensions.append(extension.upper())
        full_extensions.append(extension.lower())
    return full_extensions


def filter_by_extension(input, extensions):
    output = []
    for file in input:
        if file.endswith(tuple(extensions)):
            output.append(os.path.realpath(file))
    return output
    

def get_file_list(start_dir, extensions, recursive=False):
    full_dir = os.path.realpath(start_dir)
    full_extensions = format_extensions(extensions)
    logging.info("Getting file list:")
    logging.info("\troot directory: {0}".format(full_dir))
    logging.info("\tsearching extensions: {0}".format(" ".join(full_extensions)))
    logging.info("\trecursive: {0}".format(recursive))

    all_candidates = []

    if recursive:
        for root, dirs, files in os.walk(full_dir):
            for name in files:
                all_candidates.append(os.path.join(root, name))
            for name in dirs:
                all_candidates.append(os.path.join(root, name))
    else:
        all_candidates = os.listdir(full_dir)
            

    files = filter_by_extension(all_candidates, full_extensions)
    logging.debug("\tFound files:\n\t\t{0}".format("\n\t\t".join(files)))
    return files

def main():
    arg_parser = argparse.ArgumentParser(description="Rename images so that new name is its date/time taken.")
    arg_parser.add_argument("-v", "--verbose", action="store_true", help="Be verbose")
    arg_parser.add_argument("-C", "--directory", nargs=1, default=".", required=False, help="Specify a working directory.", metavar="directory")
    arg_parser.add_argument("-e", "--extensions", action="append", nargs=1, required=False, help="Specify file extensions.", metavar="extensions")
    arg_parser.add_argument("-r", "-R", "--recursive", action="store_true", help="Find images recursively")
    # arg_parser.add_argument("-o", "--output", default=".", help="Specify output directory", metavar="directory")
    arg_parser.add_argument("-z", "--create-dirs", action="store_true", help="Create separate directiories for each day and camera")

    args = arg_parser.parse_args()

    setup_logging(args.verbose)

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
    
    files = get_file_list(args.directory, extensions_list, recursive=args.recursive)

    utilities.rename.rename_files(files, args.create_dirs)
    return
    



if __name__ == '__main__':
    main()
