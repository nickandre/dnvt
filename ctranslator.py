


if __name__ == '__main__':
    with open('notinservice.hex', 'r') as f:
        data = f.read()
    with open('notinservice.h', 'w') as f:
        i = 0
        total_words = 0
        f.write('u_int32_t recording[] = {\n0x')
        for nibble in data:
            if i > 7:
                i = 0
                f.write(',\n0x')
                total_words += 1
            f.write(nibble)
            i += 1
        f.write('};')
        print(f'total words {total_words}')