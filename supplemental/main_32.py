# This is a sample Python script.
import wave
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import matplotlib.pyplot as plt
import numpy as np
import sys

def dnvt_to_pcm(data):
    gains = []
    output = []
    bits = []
    output_graph = []
    time=[]
    index=0;
    current_value = 0
    coincidence_counter = 0
    ones_count = 0;
    zeros_count = 0;
    min_gain = 500
    gain = min_gain
    one_instances = 0
    zero_instances = 0
    coincidences = 0
    prev_value = 0
    for nibble in data:
        bin = int(nibble, 16)
        for i in range(4):
            bitmask = 0b1 << (3 - i)
            current_bit = 1 if bin & bitmask else 0
            if abs(coincidence_counter) >= 3:
                if gain < 9000:
                    gain += 300 

                coincidences += 1
                coincidence_counter=0
            # max frequency is 3.4 khz for 16khz frequency
            # that's 5 samples where we need to get from 0, to top, to bottom, to 0 or 2x total counter
            # therefore max gain reasonable is roughly 2^16/2
            # if gain > 32767:
            #     gain = 32767
            # if gain < -32768:
            #     gain = -32768
            prev_value = current_value
            if current_bit == 1:
                one_instances += 1
                if coincidence_counter < 0:
                    coincidence_counter = 1
                else:
                    coincidence_counter += 1
                current_value += gain
            else:
                zero_instances += 1
                if coincidence_counter > 0:
                    coincidence_counter = -1
                else:
                    coincidence_counter -= 1
                current_value -= gain
            if current_value > 32767:
                current_value = 32767
            elif current_value < -32768:
                current_value = -32768

            #if gain > 3:
            #    gain -= 2
            current_value*=0.96
            gains.append(gain)
            time.append(index/32000)
            bits.append(current_bit)
            index+=1
            if gain > min_gain:
                gain *= 0.99
            if index >1:
                current_value = current_value*0.4+prev_value*0.6
            output.append(int(current_value).to_bytes(2, 'little', signed=True))
            output_graph.append(current_value)
    print(f'coincidences {coincidences} samples {len(data) * 4}')
    imbalance = abs(one_instances - zero_instances)
    imbalance_percent = imbalance/(one_instances + zero_instances)*100
    print(f'Ones: {one_instances} Zeros: {zero_instances} Imbalance {imbalance} = {imbalance_percent} %')

    ax1 = plt.subplot(311)
    plt.plot(time, gains)

    # share x axis
    ax2 = plt.subplot(312, sharex=ax1)
    plt.plot(time, output_graph)
    #plt.xlim(0.0, 0.08)
    # share x axis
    ax3 = plt.subplot(313, sharex=ax1)
    plt.plot(time, bits)
    #plt.xlim(0.0, 0.08)
    plt.show()

    return output



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    with open('FDAA10255E.txt', 'r') as f: #FDAA10255E
        data = f.read()
    with wave.open('fdaa.wav', 'wb') as f:
        f.setsampwidth(2)
        f.setnchannels(1)
        f.setframerate(32000)
        pcm_data = dnvt_to_pcm(data)
        for frame in pcm_data:
            f.writeframes(frame)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
