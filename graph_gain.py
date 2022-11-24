import matplotlib.pyplot as plt


if __name__ == '__main__':
    gain_list = []
    gain = 1
    for i in range(0, 500):
        modulo = i % 10
        if modulo == 1 or modulo == 4 or modulo == 7:
            #if gain < 15:
            gain += 0.7
            # elif gain < 18:
            #     gain += 0.25
            # elif gain < 20:
            #     gain += 0.1
        if gain > 1:
            gain /= 1.01033
        gain_list.append(gain)

    for i in range(0, 500):
        if gain > 1:
            gain /= 1.01033
        gain_list.append(gain)
    plt.plot(range(0,1000), gain_list)
    plt.show()