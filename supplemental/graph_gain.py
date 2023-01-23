import matplotlib.pyplot as plt


if __name__ == '__main__':
    gain_list = []
    syllabic_gain = 0
    min_step = 20
    for i in range(0, 500):
        modulo = i % 10
        if modulo == 1 or modulo == 4 or modulo == 7:
            #if gain < 15:
            syllabic_gain += 320
            # elif gain < 18:
            #     gain += 0.25
            # elif gain < 20:
            #     gain += 0.1
        syllabic_gain *= 0.9937694
        slope = min_step + syllabic_gain/4
        gain_list.append(slope)

    for i in range(0, 500):
        syllabic_gain *= 0.9937694
        slope = min_step + syllabic_gain / 4
        gain_list.append(slope)
    plt.plot(range(0, 1000), gain_list)
    plt.show()