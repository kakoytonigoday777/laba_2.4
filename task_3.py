import struct

def process_numbers_inplace(filepath):
    divisor = 73 ** 2 + 29   # = 5358
    with open(filepath, 'r+b') as f:
        while True:
            pos = f.tell()
            data = f.read(4)
            if len(data) < 4:
                break
            number = struct.unpack('<i', data)[0]
            if number % 7 == 0:
                new_value = int(number * 100 / divisor)
                f.seek(pos)
                f.write(struct.pack('<i', new_value))
                f.flush()
                print(f"Число {number} заменено на {new_value}")

def print_numbers(filepath):
    with open(filepath, 'rb') as f:
        print("Содержимое файла после обработки:")
        while True:
            data = f.read(4)
            if not data:
                break
            num = struct.unpack('<i', data)[0]
            print(num, end=' ')
        print()

if __name__ == '__main__':
    process_numbers_inplace('resource/numbers.bin')
    print_numbers('resource/numbers.bin')