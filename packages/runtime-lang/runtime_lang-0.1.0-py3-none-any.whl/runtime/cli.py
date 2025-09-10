from . import runtime
from sys import exit, argv
import os

BASE_DIRECTORY = os.getcwd()

def main():
    if len(argv) == 1:
        repl()
    else:
        file_name = argv[1].strip()
        run(file_name)

def run(file_name, log = True):
    try:
        path = os.path.join(BASE_DIRECTORY, "programs", file_name)
        if not os.path.exists(path) and not path.endswith('.run'): path = path + '.run'

        with open(path, 'r') as file:
            text = file.read()

            result, error = runtime.run(file_name, text)
            if error: print(error)
        
    except KeyboardInterrupt:
        exit(0)

    except FileNotFoundError:
        display_name = file_name if file_name.endswith('.run') else file_name + '.run'
        print(f"Could not open file: programs/{display_name}")

def repl():
    while True:
        file_name = '<stdin>'

        try:
            text = input('RUNTIME > ')

            if text.strip() == '':
                continue
        except KeyboardInterrupt:
            exit(0)

        result, error = runtime.run(file_name, text)

        if error: print(error)
        else:
            if isinstance(result, runtime.List) and len(result.value) == 1:
                print(repr(result.value[0]))
            else:
                print(repr(result))