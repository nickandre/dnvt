
resistor_values = [
    1,
    1,
    1,
    1,
    3,
    1,
    7,
    1,
    15,
    1,
    31,
    1,
    63,
    1,
    127,
]

vr1_resistor_selection = [
    0,
    1,
    3,
    5,
    7,
    9,
    11,
    13
]

vr2_resistor_selection = [
    -1,
    0,
    2,
    4,
    6,
    8,
    10,
    12
]
RESISTOR_TOTAL = sum(resistor_values)
capacitor_values = range(0, 16)

def calculate_capacitance(capacitors):
    result = 0
    if capacitors & 0b1:
        result += 1
    if capacitors & 0b10:
        result += 2
    if capacitors & 0b100:
        result += 4
    if capacitors & 0b1000:
        result += 8
    return result

if __name__ == '__main__':
    gain_list = []
    for i in range(0, 128):
        h_index = hex(i)
        selected_resistor = int((i & 0b1110000) >> 4)
        selected_capacitors = i & 0b1111
        capacitance = calculate_capacitance(selected_capacitors)
        # for slice sum, we need index + 1 to sum from first to index
        vr1_index = vr1_resistor_selection[selected_resistor] + 1
        # vr2 is offset by one msb, i.e. one decoder value lower
        vr2_index = vr2_resistor_selection[selected_resistor] + 1
        vr1 = sum(resistor_values[0:vr1_index])
        vr2 = sum(resistor_values[0:vr2_index])
        k2c = 1
        # equation: vr1 * (CT / k2c) + vr2 * (16C / k2c)
        # equation: vr1 * (capacitance / 1) + vr2 * 16c / 1
        gain = vr1 * capacitance + vr2 * 16
        gain_list.append(gain)
        print(f'{gain}')
        #print(f'vr1: {vr1} {vr1_index} vr2: {vr2} selected capacitors: {capacitance}')
    print(gain_list)
    resistor_running_total = 0
    for r in resistor_values:
        resistor_running_total += r
        for c in capacitor_values:
            vr1 = r / RESISTOR_TOTAL

            # paper lists function
            #  (CT / K2C) * vr1 + (16C/K2C) * vr2
            # CT = total selected capacitance
            #