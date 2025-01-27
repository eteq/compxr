import pathlib
import time
import subprocess
import selectors

import numpy as np


class FailedReaderError(Exception):
    pass

class QuaternionHistory:
    def __init__(self, history_size=20, dtype=np.float32):
        self.buffer = np.zeros((history_size, 4), dtype=dtype)
        self.current_index = -1
        self.filled_once = False

    def process_line(self, line):
        bytes_wxyz = line[5:21]
        wxyz = np.frombuffer(bytes_wxyz, dtype=self.buffer.dtype)
        self.current_index = (self.current_index + 1) % self.buffer.shape[0]
        self.buffer[self.current_index] = wxyz
        if (self.current_index + 1) == self.buffer.shape[0]:
            self.filled_once = True

    def get_ordered_history(self):
        """
        yields the quaternion set (wxyz) with the most recent at the end of the array
        """
        return np.roll(self.buffer, (self.buffer.shape[0]-1)-self.current_index, axis=0)
    

def main(execpath, nignore_initial, nhistory, dump):
    quats = QuaternionHistory(history_size=nhistory)

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

                    quats.process_line(fulline)
                    if quats.filled_once:
                        if dump is not None:
                            np.savetxt(dump, quats.get_ordered_history(), delimiter=',')
                            print('dumped', quats.buffer.shape[0], f'quaternions to {dump}, exiting.')
                            return
                        else:
                            raise NotImplementedError()

                    #$print('loops overhead:', loops_since_last_processing) # DEBUG: use this to monitor how much time is free
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
        time.sleep(0.001) # this really shouldn't be necessary with select but for some reason it's not sleeping up there?


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--execpath', default='build/viture-logger')
    parser.add_argument('--nignore-initial', default=120, type=int)
    parser.add_argument('--nhistory', default=20, type=int)
    parser.add_argument('--dump', default=pathlib.Path('.'), type=pathlib.Path)

    args = parser.parse_args()
    if str(args.dump) == '.':
        args.dump = None

    main(args.execpath, args.nignore_initial, args.nhistory, args.dump)
