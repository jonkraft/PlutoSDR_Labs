
import sys
sys.path.append('C:\\Users\\jkraft\\AppData\\Local\\Programs\\Python\\Python37-32\\Lib\\site-packages\\')
#sys.path.append('C:\\Users\\jkraft\\AppData\\Local\\Programs\\Python\\Python37-32\\Lib\\site-packages\\libiio-0.18\\bindings\\python\\')
sys.path.append('C:\\Users\\jkraft\\AppData\\Local\\Programs\\Python\\Python39\\Lib\\site-packages\\libiio-0.21\\bindings\\python\\')
#import iio

"""
modified from https://github.com/analogdevicesinc/pyadi-iio/blob/ensm-example/examples/pluto.py

"""

import adi
import time
import matplotlib.pyplot as plt
import numpy as np

# Create radio
sdr = adi.ad9361(uri='ip:192.168.2.1')
samp_rate = 30.72e6    # must be <=30.72 MHz if both channels are enabled
num_samps = 2**18      # number of samples per buffer.  Can be different for Rx and Tx
rx_lo = 1e9
rx_mode = "slow_attack"  # can be "manual" or "slow_attack"
rx_gain0 = 10
rx_gain1 = 10
tx_lo = rx_lo
tx_gain0 = -10
tx_gain1 = -10

'''Configure Rx properties'''
sdr.rx_enabled_channels = [0, 1]
sdr.sample_rate = int(samp_rate)
sdr.rx_lo = int(rx_lo)
sdr.gain_control_mode = rx_mode
sdr.rx_hardwaregain_chan0 = int(rx_gain0)
sdr.rx_hardwaregain_chan1 = int(rx_gain1)
sdr.rx_buffer_size = int(num_samps)

'''Configure Tx properties'''
sdr.tx_rf_bandwidth = int(samp_rate)
sdr.tx_lo = int(tx_lo)
sdr.tx_cyclic_buffer = True
sdr.tx_hardwaregain_chan0 = int(tx_gain0)
sdr.tx_hardwaregain_chan1 = int(tx_gain1)
sdr.tx_buffer_size = int(num_samps)

# Example read properties
print("RX LO %s" % (sdr.rx_lo))

# Program the Tx with some data
fs = int(sdr.sample_rate)
fc0 = int(2e6)
fc1 = int(5e6)
N = 2**16
ts = 1 / float(fs)
t = np.arange(0, N * ts, ts)
i0 = np.cos(2 * np.pi * t * fc0) * 2 ** 14
q0 = np.sin(2 * np.pi * t * fc0) * 2 ** 14
i1 = np.cos(2 * np.pi * t * fc1) * 2 ** 14
q1 = np.sin(2 * np.pi * t * fc1) * 2 ** 14
iq0 = i0 + 1j * q0
iq1 = i1 + 1j * q1
sdr.tx([iq0, iq1])   # Send Tx data.  But don't use this if the dds generator is enabled above.  You can only send data with one method, not both!!

# Collect data
for r in range(20):    # grab several buffers to give the AGC time to react (if AGC is set to "slow_attack" instead of "manual")
    data = sdr.rx()

Rx_0=data[0]
Rx_1=data[1]
Rx_total = Rx_0 + Rx_1
NumSamples = len(Rx_total)
win = np.hamming(NumSamples)
y = Rx_total * win
sp = np.absolute(np.fft.fft(y))
sp = sp[1:-1]
sp = np.fft.fftshift(sp)
s_mag = np.abs(sp) / (np.sum(win)/2)    # Scale FFT by window and /2 since we are using half the FFT spectrum
s_dbfs = 20*np.log10(s_mag/(2**12))     # Pluto is a 12 bit ADC, so use that to convert to dBFS
xf = np.fft.fftfreq(NumSamples, ts)
xf = np.fft.fftshift(xf[1:-1])/1e6
plt.plot(xf, s_dbfs)
plt.xlabel("frequency [MHz]")
plt.ylabel("dBfs")
plt.draw()
plt.show()





