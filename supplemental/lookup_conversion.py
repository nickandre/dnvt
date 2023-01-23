# This is a sample Python script.
import wave
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

gain_table = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 52, 56, 60, 64, 68, 72, 76, 80, 84, 88, 92, 96, 100, 104, 108, 112, 120, 128, 136, 144, 152, 160, 168, 176, 184, 192, 200, 208, 216, 224, 232, 240, 256, 272, 288, 304, 320, 336, 352, 368, 384, 400, 416, 432, 448, 464, 480, 496, 528, 560, 592, 624, 656, 688, 720, 752, 784, 816, 848, 880, 912, 944, 976, 1008, 1072, 1136, 1200, 1264, 1328, 1392, 1456, 1520, 1584, 1648, 1712, 1776, 1840, 1904, 1968, 2032, 2160, 2288, 2416, 2544, 2672, 2800, 2928, 3056, 3184, 3312, 3440, 3568, 3696, 3824, 3952]

def dnvt_to_pcm(data, output_file):
    output = []
    current_value = 0
    coincidence_counter = 0
    ones_count = 0
    zeros_count = 0
    max_gain = 0
    gain = 0
    one_instances = 0
    zero_instances = 0
    coincidences = 0
    clips = 0
    for nibble in data:
        bin = int(nibble, 16)
        for i in range(4):
            bitmask = 0b1 << (3 - i)
            current_bit = 1 if bin & bitmask else 0
            if abs(coincidence_counter) >= 3:
                if gain < 127:
                    gain += 1
                else:
                    max_gain += 1

                coincidences += 1
            elif gain > 0:
                gain -= 1
                #coincidence_counter=0
            # max frequency is 3.4 khz for 16khz frequency
            # that's 5 samples where we need to get from 0, to top, to bottom, to 0 or 2x total counter
            # therefore max gain reasonable is roughly 2^16/2
            # if gain > 32767:
            #     gain = 32767
            # if gain < -32768:
            #     gain = -32768
            if current_bit == 1:
                one_instances += 1
                if coincidence_counter < 0:
                    coincidence_counter = 1
                else:
                    coincidence_counter += 1
                current_value += (gain_table[gain] + 1) * 250
            else:
                zero_instances += 1
                if coincidence_counter > 0:
                    coincidence_counter = -1
                else:
                    coincidence_counter -= 1
                current_value -= (gain_table[gain] + 1) * 250
            if current_value > 32767:
                current_value = 32767
                clips += 1
            elif current_value < -32768:
                current_value = -32768
                clips += 1

            #if gain > 3:
            #    gain -= 2
            current_value *= 0.99
            if gain > 0 and abs(coincidence_counter) < 4:
                gain -= 1
            output_file.writeframes(int(current_value).to_bytes(2, 'little', signed=True))
        #output.append(int(current_value).to_bytes(2, 'little', signed=True))

    print(f'coincidences {coincidences} samples {len(data) * 4} clips {clips} max gain {max_gain}')
    imbalance = abs(one_instances - zero_instances)
    imbalance_percent = imbalance/(one_instances + zero_instances)*100
    print(f'Ones: {one_instances} Zeros: {zero_instances} Imbalance {imbalance} = {imbalance_percent} %')
    return output





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    with open('notinservice.hex', 'r') as f:
        data = f.read()
    with wave.open('notinservice5.wav', 'wb') as f:
        f.setsampwidth(2)
        f.setnchannels(1)
        f.setframerate(32000)
        pcm_data = dnvt_to_pcm(data=data, output_file=f)
        #for frame in pcm_data:
            #f.writeframes(frame)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
