# Filtered 32kHz DNVT Decoder
import wave

import matplotlib.pyplot as plt
import numpy as np
import sys

def dnvt_to_pcm(data):
    gains               = []
    output              = []
    bits                = []
    output_graph        = []
    output_filtered     = []
    time                = []
    coincidence_graph   = []
    index               = 0
    current_value       = 0
    coincidence_counter = 0
    ones_count          = 0
    zeros_count         = 0
    one_instances       = 0
    zero_instances      = 0
    coincidences        = 0
    syllabic_gain       = 0

    #Setting tuning parameters
    parameters = "rob"
    #parameters = "lincoln"
    if(parameters == "rob"):
        min_gain            = 100 
        gain_fraction       = 0.3
        gain_step           = int(min_gain*gain_fraction) #30
        coincidence_valid   = 3
        signal_decay        = 0.96
        gain_decay          = 0.99
        max_gain            = 18000
        gain = min_gain + syllabic_gain
    if(parameters == "lincoln"):
        min_gain            = 20 #"DELTA_MIN"
        gain_step           = int(310/4) #"DELTA_MAX" = 77
        coincidence_valid   = 3
        signal_decay        = 0.9692332 #"PRINCIPAL_T"
        gain_decay          = 0.9937694 #"SYLLABIC_T"
        max_gain            = 18000
        gain = min_gain + syllabic_gain

    for nibble in data:
        bin = int(nibble, 16)
        for i in range(4):
            bitmask = 0b1 << (3 - i)
            current_bit = 1 if bin & bitmask else 0

            #Update coincidence counting
            if current_bit == 1:
                one_instances += 1
                if coincidence_counter < 0:
                    coincidence_counter = 1
                else:
                    coincidence_counter += 1
            else:
                zero_instances += 1
                if coincidence_counter > 0:
                    coincidence_counter = -1
                else:
                    coincidence_counter -= 1

            #Update syllabic gain (based on coincidence)
            if abs(coincidence_counter) >= coincidence_valid:
                coincidences += 1
                if syllabic_gain < max_gain:
                    syllabic_gain += gain_step 
            gain = min_gain + syllabic_gain
            #Update Output:
            if current_bit == 1:
                current_value += gain
            else:
                current_value -= gain

            #Clip signal:
            if current_value > 32767:
                current_value = 32767
            elif current_value < -32768:
                current_value = -32768

            #Append to outputs
            #output.append(int(current_value).to_bytes(2, 'little', signed=True))
            output_graph.append(current_value)
            coincidence_graph.append(coincidence_counter)
            time.append(index/32000)
            bits.append(current_bit)
            gains.append(gain)
            index+=1

            #Update gains
            current_value *=signal_decay
            syllabic_gain *=gain_decay

    prevval1 = 0
    prevval2 = 0
    for i in output_graph:
        filtval = 0.33*prevval1+0.33*prevval2+0.34*i
        output_filtered.append(filtval)
        prevval2 = prevval1
        prevval1 = i
        output.append(int(filtval).to_bytes(2, 'little', signed=True))
    print(f'coincidences {coincidences} samples {len(data) * 4}')
    imbalance = abs(one_instances - zero_instances)
    imbalance_percent = imbalance/(one_instances + zero_instances)*100
    print(f'Ones: {one_instances} Zeros: {zero_instances} Imbalance {imbalance} = {imbalance_percent} %')
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, constrained_layout=True, sharex=True)
    ax1.plot(time, gains)
    #ax1.ylabel('Counts')
    #plt.xlabel('Time (seconds)')
    # share x axis
    ax2.plot(time, output_graph, time, output_filtered)
    #ax2.ylabel('Counts')
    #plt.xlabel('Time (seconds)')
    #plt.xlim(0.0, 0.08)
    # share x axis
    ax3.plot(time, coincidence_graph)
    #plt.xlim(0.0, 0.08)
    plt.ylabel('Counts')
    plt.xlabel('Time (seconds)')
    ax1.set_title('Gain')
    ax2.set_title('Output')
    ax3.set_title('Coincidence Counter')
    plt.show()

    return output


if __name__ == '__main__':
    with open('FDAA10255E.txt', 'r') as f: #FDAA10255E
        data = f.read()
    with wave.open('tone_test.wav', 'wb') as f:
        f.setsampwidth(2)
        f.setnchannels(1)
        f.setframerate(32000)
        pcm_data = dnvt_to_pcm(data)
        for frame in pcm_data:
            f.writeframes(frame)