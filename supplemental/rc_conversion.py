# This is a sample Python script.
import wave
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

SCALE = 500
LINEAR_THRESHOLD = 0.8
SECOND_THRESHOLD = 0.9
MAX_GAIN = 20
def dnvt_to_pcm(data, file):
    #output = []
    current_value = 0
    coincidence_counter = 0
    ones_count = 0
    zeros_count = 0
    gain = 1
    one_instances = 0
    zero_instances = 0
    coincidences = 0
    for nibble in data:
        bin = int(nibble, 16)
        for i in range(4):
            bitmask = 0b1 << (3 - i)
            current_bit = 1 if bin & bitmask else 0
            if abs(coincidence_counter) >= 3:
                # 30% coincidence requires 90% of 18 after 10ms or 320 samples
                # 96 coincidences from 320 samples
                # per testing in graph_gain.py, 30% coincidence with 0.7 and gain /= 1.01033
                # hits 18
                if gain < MAX_GAIN:
                    gain += 0.7
                # if gain < LINEAR_THRESHOLD * MAX_GAIN:
                #     gain += 0.4
                # elif gain < SECOND_THRESHOLD * MAX_GAIN:
                #     gain += 0.1
                # elif gain < MAX_GAIN:
                #     gain += 0.01

                coincidences += 1

            if current_bit == 1:
                one_instances += 1
                if coincidence_counter < 0:
                    coincidence_counter = 1
                else:
                    coincidence_counter += 1
                current_value += gain * SCALE
            else:
                zero_instances += 1
                if coincidence_counter > 0:
                    coincidence_counter = -1
                else:
                    coincidence_counter -= 1
                current_value -= gain * SCALE
            if current_value > 32767:
                current_value = 32767
            elif current_value < -32768:
                current_value = -32768

            current_value*=0.99

            # decay:
            # 7 ms for 90% decay, that means 224 samples
            # 0.1 = (1/x)^224, x = 1.01033
            if gain > 1:
                gain /= 1.01033
        f.writeframes(int(current_value).to_bytes(2, 'little', signed=True))

    print(f'coincidences {coincidences} samples {len(data) * 4}')
    imbalance = abs(one_instances - zero_instances)
    imbalance_percent = imbalance/(one_instances + zero_instances)*100
    print(f'Ones: {one_instances} Zeros: {zero_instances} Imbalance {imbalance} = {imbalance_percent} %')





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    with open('notinservice.hex', 'r') as f:
        data = f.read()
    with wave.open('notinservice-rc8k.wav', 'wb') as f:
        f.setsampwidth(2)
        f.setnchannels(1)
        f.setframerate(8000)
        dnvt_to_pcm(data, f)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
