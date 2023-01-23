

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    with open('notinservice.hex', 'r') as f:
        data = f.read()
    with open('notinservice.cvs', 'wb') as f:
        int()
        f.write(bytearray.fromhex(data))
        # for c in data:
        #     scale = 16  ## equals to hexadecimal
        #     num_of_bits = 8

