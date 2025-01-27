import subprocess
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK


def main(execpath):
    process = subprocess.Popen(execpath, stdout=subprocess.PIPE)

    # switch stdout to non-blocking mode so we can do processing while waiting
    fcntl(p.stdout, F_SETFL, fcntl(process.stdout, F_GETFL) | O_NONBLOCK)


    raise NotImplementedError()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--execpath', default='./viture-logger')

    args = parser.parse_args()

    main(args.execpath)