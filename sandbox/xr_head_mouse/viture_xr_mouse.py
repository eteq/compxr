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

    # register a selector to check for input
    sel = selectors.DefaultSelector()
    sel.register(process.stdout, selectors.EVENT_READ)

    lastread = time.time()
    i = 0
    while True:
        i += 1
        for key, _ in sel.select(timeout=0):
            line = key.fileobj.readline()
            nowread = time.time()
            print('read line with length', len(line), 'w/ delay', (nowread - lastread)*1e3, 'ms, loop runs', i)
            lastread = nowread
            i = 0

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--execpath', default='build/viture-logger')

    args = parser.parse_args()

    main(args.execpath)
