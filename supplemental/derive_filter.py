import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

if __name__ == '__main__':
    #sos = signal.cheby1(N=6, rp=2, Wn=4000, output='sos', fs=32000)
    sos = signal.iirfilter(6, [5000], rs=40, btype='lowpass',
                           analog=False, ftype='cheby2', fs=32000,
                           output='sos')
    w, h = signal.sosfreqz(sos, 32000, fs=32000)
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.semilogx(w, 20 * np.log10(np.maximum(abs(h), 1e-5)))
    ax.set_title('Chebyshev Type II bandpass frequency response')
    ax.set_xlabel('Frequency [Hz]')
    ax.set_ylabel('Amplitude [dB]')
    ax.axis((10, 16000, -100, 10))
    ax.grid(which='both', axis='both')
    plt.show()