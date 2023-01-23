# 32 kbps CVSD Decoder for Digital Non-secure Voice Terminals with IIR Filtering
# 
# Nick Andre and Robert Ruark
# 2023

import wave

from scipy import signal
from scipy.fft import fft, fftfreq

SCALE = 250
LINEAR_THRESHOLD = 0.8
SECOND_THRESHOLD = 0.9
MAX_GAIN = 20
def dnvt_to_pcm(data, file):
    current_value = 0
    coincidence_counter = 0
    ones_count = 0
    zeros_count = 0
    gain = 0
    one_instances = 0
    zero_instances = 0
    coincidences = 0
    previous_filtered = 0
    sample = 0
    sos = signal.iirfilter(6, [5000], rs=40, btype='lowpass',
                           analog=False, ftype='cheby2', fs=32000,
                           output='sos')
    zi = signal.sosfilt_zi(sos)
    for nibble in data:
        bin = int(nibble, 16)
        for i in range(4):
            bitmask = 0b1 << (3 - i)
            current_bit = 1 if bin & bitmask else 0
            if abs(coincidence_counter) >= 3:
                if gain < MAX_GAIN:
                    gain += 0.72

                coincidences += 1

            if current_bit == 1:
                one_instances += 1
                if coincidence_counter < 0:
                    coincidence_counter = 1
                else:
                    coincidence_counter += 1
                current_value += (gain + 1) * SCALE
            else:
                zero_instances += 1
                if coincidence_counter > 0:
                    coincidence_counter = -1
                else:
                    coincidence_counter -= 1
                current_value -= (gain + 1) * SCALE

            current_value *= 0.98

            # decay:
            # 7 ms for 90% decay, that means 224 samples
            # 0.1 = (1/x)^224, x = 1.01033
            #gain /= 1.01033
            gain *= 0.9875778
            # The de-emphasis IIR filter implemented here is:
            # H(z) = 1 / (1 - az^-1) for 0.92 < a < 0.98
            # Y/X = 1/ (1 - az^-1)
            # Y(1 - az^-1) = X
            # y[n] - ay[n-1] = x[n]
            # y[n] = x[n] + ay[n-1]
            a = 0.90
            filtered_val = (current_value + previous_filtered * a) / 2 # + prev2_val * 0.33
            previous_filtered = filtered_val
            y_sos, zi = signal.sosfilt(sos=sos, x=[filtered_val], zi=zi)
            fir_val = y_sos[0]
            if fir_val > 32767:
                fir_val = 32767
            elif fir_val < -32768:
                fir_val = -32768
            #if i % 4 == 0:
            f.writeframes(int(fir_val).to_bytes(2, 'little', signed=True))
            i += 1

    print(f'coincidences {coincidences} samples {len(data) * 4}')
    imbalance = abs(one_instances - zero_instances)
    imbalance_percent = imbalance/(one_instances + zero_instances)*100
    print(f'Ones: {one_instances} Zeros: {zero_instances} Imbalance {imbalance} = {imbalance_percent} %')
    # from scipy.fft import fft, fftfreq
    #
    # # Number of samples in normalized_tone
    # N = SAMPLE_RATE * DURATION
    #
    # yf = fft(normalized_tone)
    # xf = fftfreq(N, 1 / SAMPLE_RATE)
    #
    # plt.plot(xf, np.abs(yf))
    # plt.show()

if __name__ == '__main__':
    with open('cvsd_data/genesis_reencoded.hex', 'r') as f:
        data = f.read()
    with wave.open('wav_data/genesis_redecoded.wav', 'wb') as f:
        f.setsampwidth(2)
        f.setnchannels(1)
        f.setframerate(32000)
        dnvt_to_pcm(data, f)