import numpy as np

import time
import subprocess
import selectors

class FailedReaderError(Exception):
    pass


def process_line(line):
    # wb = line[5:9]
    # xb = line[9:13]
    # yb = line[13:17]
    # zb = line[17:21]
    buffer_wxyz = line[5:21]
    wxyz = np.frombuffer(buffer_wxyz, dtype=np.float32)
    print(wxyz)

def main(execpath, nignore_initial):

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

    fulline = b''
    completed_lines = 0
    loops_since_last_processing = 0
    nzeros = 0
    while True:
        for key, _ in sel.select(timeout=0):
            line = key.fileobj.readline()
            if line.startswith(b'start'):
                if len(fulline) > 0:
                    print('reached a start without a completed line! possible error in viture reading process.')
                fulline = line
            else:
                fulline += line
            if len(fulline) == 22:
                if not fulline.startswith(b'start'):
                    print('got a line that does not start with start! Skipping...')
                else:
                    completed_lines += 1
                    if completed_lines <= nignore_initial:
                        fulline = b''
                        continue
                    process_line(fulline)
                    print('loops overhead:', loops_since_last_processing)
                    if loops_since_last_processing == 0:
                        nzeros += 1
                    else:
                        nzeros = 0
                    if nzeros > 1:
                        print("the viture process may be outpacing python... consecutive immediate reads:", nzeros)
                    loops_since_last_processing = -1
                fulline = b''
            elif len(fulline) > 22:
                print('line overflowed!')
                fulline = b''
        loops_since_last_processing += 1


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--execpath', default='build/viture-logger')
    parser.add_argument('--nignore-initial', default=120, type=int)

    args = parser.parse_args()

    main(args.execpath, args.nignore_initial)
