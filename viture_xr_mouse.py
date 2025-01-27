import time
import subprocess
import selectors

class FailedReaderError(Exception):
    pass

def main(execpath):

    process = subprocess.Popen(execpath, stdout=subprocess.PIPE)

    # give it some time to initialize or fail
    time.sleep(1)
    pollres = process.poll()
    if pollres is not None:
        if pollres == 52:
            raise FailedReaderError('viture device init failed')
        else:
            raise FailedReaderError(f'viture reader process failed with code {pollres}')

    # switch stdout to non-blocking mode so we can do processing while waiting
    #fcntl(p.stdout, F_SETFL, fcntl(process.stdout, F_GETFL) | O_NONBLOCK)

    # register a selector to check for input
    sel = selectors.DefaultSelector()
    sel.register(process.stdout, selectors.EVENT_READ)

    lastread = time.time()
    while True:
        for key, _ in sel.select():
            line = key.fileobj.readline()
            nowread = time.time()
            print('read line with length', len(line), 'delay', nowread - lastread)
            lastread = nowread

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--execpath', default='build/viture-logger')

    args = parser.parse_args()

    main(args.execpath)