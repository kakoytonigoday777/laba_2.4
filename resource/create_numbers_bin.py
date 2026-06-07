import struct

def create_numbers_bin(filepath, numbers):
    with open(filepath, 'wb') as f:
        for num in numbers:
            f.write(struct.pack('<i', num))
    print(f"Файл {filepath} создан с числами: {numbers}")

if __name__ == '__main__':
    test_numbers = [1, 7, 3, 14, 5, 21, 8, 28, 10]
    create_numbers_bin('numbers.bin', test_numbers)