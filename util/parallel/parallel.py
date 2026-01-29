# %%
import time
import threading

from . import setPortAddress, setData

# %%

# %%


class Parallel(object):
    def __init__(self):
        self.address = None
        pass

    def reset(self, address):
        self.address = address
        address_hex = int(address, 16)
        setPortAddress(address_hex)
        setData(0)
        self.latest = 0

    def send(self, value, verbose=True):
        if self.address is None:
            print('Send failed since the Parallel is not set')
            return

        t = threading.Thread(target=self._send, args=(
            value, verbose), daemon=True)
        t.start()

        return time.time()

    def _send(self, value, verbose):
        try:
            value = int(value)
        except Exception as err:
            print('Exception: %s' % err)
            value = self.latest + 1

        setData(value)
        time.sleep(0.001)
        setData(0)

        self.latest = value
        if verbose:
            print('Sent: {} to {}'.format(value, self.address))
