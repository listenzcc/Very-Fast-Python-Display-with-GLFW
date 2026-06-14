'''
Doc:
    <https://www.psychopy.org/hardware/egiNetStation.html>

Install:
    pip install egi-pynetstation
'''

# %%
# Import Netstation library
import time
from egi_pynetstation.NetStation import NetStation

print(NetStation)

# %%
# IP address of NetStation - CHANGE THIS TO MATCH THE IP ADDRESS OF YOUR NETSTATION
IP_ns = '10.10.10.42'  # Network Address

# IP address of amplifier (if using 300
# series, this is the same as the IP address of
# NetStation. If using newer series, the amplifier
# has its own IP address)
IP_amp = '10.10.10.51'  # Client Address

# Port configured for ECI in NetStation - CHANGE THIS IF NEEDED
port_ns = 55513

# Start recording and send trigger to show this
eci_client = NetStation(IP_ns, port_ns)
eci_client.connect(ntp_ip=IP_amp)
eci_client.begin_rec()
eci_client.send_event(event_type='STRT', start=0.0)

# Sending loop
# todo: not well tested
for _ in range(10):
    eci_client.resync()
    print('Sending')
    eci_client.send_event(event_type='stim', label='stim')
    print('Sent')
    time.sleep(1)

# Stop recording and disconnect
eci_client.end_rec()
eci_client.disconnect()

# %%
