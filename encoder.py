# This is a sample Python script.
import wave

from scipy import signal
from scipy.fft import fft, fftfreq
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

SCALE = 250
LINEAR_THRESHOLD = 0.8
SECOND_THRESHOLD = 0.9
MAX_GAIN = 20

def pcm_to_dnvt(input, output):
    current_value = 0
    coincidence_counter = 0
    ones_count = 0
    zeros_count = 0
    gain = 0
    one_instances = 0
    zero_instances = 0
    coincidences = 0
    sample = 0
    frames = input.getnframes()
    max_frames = 500000
    previous_pcm = 0
    for i in range(max_frames):
        #TODO: burn first byte
        bit_index = 7 - (i % 8)
        frame = input.readframes(1)
        pcm_value = int.from_bytes(frame, 'little', signed=True)
        # Y/X = 1 - a*z^-1
        # Y = X - Xaz^-1
        # y[n] = x[n] - ax[n-1]
        a = 0.90
        filtered_pcm_val = (pcm_value - previous_pcm * a)  # + prev2_val * 0.33
        previous_pcm = pcm_value
        if filtered_pcm_val >= current_value:
            current_bit = 1
        else:
            current_bit = 0
        sample |= current_bit << bit_index

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
        gain *= 0.9875778



        if bit_index == 0:
            #output.write(sample.to_bytes(1, 'little'))
            output.write(f'{sample:x}')
            sample = 0

        # tODO: The de-emphasis IIR filter implemented here is:
        # H(z) = 1 / (1 - az^-1) for 0.92 < a < 0.98
        # a = 0.90
        # filtered_val = (current_value + previous_filtered * a) / 2 # + prev2_val * 0.33
        # previous_filtered = filtered_val
        # y_sos, zi = signal.sosfilt(sos=sos, x=[filtered_val], zi=zi)
        # fir_val = y_sos[0]
        # if fir_val > 32767:
        #     fir_val = 32767
        # elif fir_val < -32768:
        #     fir_val = -32768
        # #if i % 4 == 0:
        # f.writeframes(int(fir_val).to_bytes(2, 'little', signed=True))
        # i += 1

    #print(f'coincidences {coincidences} samples {len(data) * 4}')
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





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    with wave.open('rick-4k.wav', 'rb') as input:
        with open('rick-c.hex', 'w') as output:
            pcm_to_dnvt(input, output)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
