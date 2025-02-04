import pathlib
import time
import subprocess
import selectors

import numpy as np
from scipy.spatial.transform import Rotation

import uinput


class FailedReaderError(Exception):
    pass

class QuaternionHistory:
    def __init__(self, history_size=20, dtype=np.float32):
        self.buffer = np.zeros((history_size, 4), dtype=dtype)
        self.current_index = -1
        self.filled_once = False

    def process_line(self, line):
        bytes_wxyz = line[5:21][::-1] # reverse the bytes to get the correct order
        wxyz = np.frombuffer(bytes_wxyz, dtype=self.buffer.dtype)[::-1] # reverse to get wxyz since we reversed the bytes above
        self.current_index = (self.current_index + 1) % self.buffer.shape[0]
        self.buffer[self.current_index] = wxyz
        if (self.current_index + 1) == self.buffer.shape[0]:
            self.filled_once = True

    def get_ordered_history(self):
        """
        yields the quaternion set (wxyz) with the most recent at the end of the array
        """
        return np.roll(self.buffer, (self.buffer.shape[0]-1)-self.current_index, axis=0)
    
def process_quats(orderedhistory, emitterdevice, dt=1/60, sensitivity=(1, 1), deadzone=None):
    dw, dx, dy, dz = np.diff(orderedhistory[-2:], axis=0)[0].T
    w0, x0, y0, z0 = np.sum(orderedhistory[-2:], axis=0)

    omega_y = 2 * (w0*dy + x0*dz - y0*dw - z0*dx)/dt
    omega_z = 2 * (w0*dz - x0*dy + y0*dx - z0*dw)/dt

    xmouse = -int(omega_z*sensitivity[0])
    ymouse = int(omega_y*sensitivity[1])

    if deadzone is not None:
        if np.abs(xmouse) < deadzone:
            xmouse = 0
        if np.abs(ymouse) < deadzone:
            ymouse = 0

    emitterdevice.emit(uinput.REL_X, xmouse, syn=False)
    emitterdevice.emit(uinput.REL_Y, ymouse)

def main(execpath, nignore_initial, nhistory, dump, print_basis, sensitivity, deadzone):
    if deadzone == 0:
        deadzone = None

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
    with uinput.Device((
        uinput.REL_X,
        uinput.REL_Y,
        uinput.BTN_LEFT,
        uinput.BTN_RIGHT,
        )) as pointingdev:
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
                        if nignore_initial is not None:
                            if completed_lines <= nignore_initial:
                                fulline = b''
                                continue
                            else:
                                print('completed', nignore_initial, 'initial ignored lines')
                                nignore_initial = None

                        quats.process_line(fulline)
                        if quats.filled_once:
                            if print_basis and ((completed_lines % print_basis) == 0):
                                rot = Rotation.from_quat(quats.buffer[quats.current_index], scalar_first=True)
                                x = rot.apply([1, 0, 0])
                                y = rot.apply([0, 1, 0])
                                z = rot.apply([0, 0, 1])
                                print(f"basis' rotated to x={x}, y={y}, z={z}")
                            if dump is not None:
                                np.savetxt(dump, quats.get_ordered_history(), delimiter=',')
                                print('dumped', quats.buffer.shape[0], f'quaternions to {dump}, exiting.')
                                return
                            else:
                                process_quats(quats.get_ordered_history(), 
                                              pointingdev, 
                                              sensitivity=sensitivity,
                                              deadzone=deadzone)

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

    fpth = pathlib.Path(__file__).parent

    parser = argparse.ArgumentParser()
    parser.add_argument('--execpath', default=fpth / 'build/viture-logger')
    parser.add_argument('--nignore-initial', default=120, type=int)
    parser.add_argument('--nhistory', default=20, type=int)
    parser.add_argument('--dump', default=pathlib.Path('.'), type=pathlib.Path)
    parser.add_argument('--print-basis', default=0, type=int)
    parser.add_argument('-x', '--sensitivity-x', default=20, type=float)
    parser.add_argument('-y', '--sensitivity-y', default=15, type=float)
    parser.add_argument('-d', '--dead-zone', default=2.5, type=float)

    args = parser.parse_args()
    if str(args.dump) == '.':
        args.dump = None

    sens = (args.sensitivity_x, args.sensitivity_y)
    main(args.execpath,
         args.nignore_initial,
         args.nhistory, 
         args.dump, 
         args.print_basis, 
         sens, 
         args.dead_zone)
