import os
import subprocess
import datetime


def main():
    version = subprocess.check_output(
        ["git", "describe"]).decode("utf-8").split("\n")[0]
    print(version)

    with open("version.py", "w") as f:
        f.write("version=\"" + version +
                " (built " + datetime.datetime.now().isoformat() + ")\"")

    os.system("pyinstaller photoman.py --clean --name mmm -F")


if __name__ == '__main__':
    main()
