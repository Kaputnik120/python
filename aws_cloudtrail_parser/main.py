import getopt
import json
import sys


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "h", ["file="])
    except getopt.GetoptError as e:
        print(e)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('--file=<search string> -h')
            sys.exit()
        if opt == '--file':
            file_path = arg

    if file_path is None:
        print('Mandatory option --file not set')
        sys.exit()

    file = open(file_path, "r")
    json_file: dict = json.load(file)

    for record in json_file['Records']:
        if 'Backup' in str(record):
            print(json.dumps(record, indent=4))
            print()


if __name__ == "__main__":
    main(sys.argv[1:])
