import struct


def create_data_bin(filepath):
    with open(filepath, 'wb') as f:
        f.write(b'DATA')

        f.write(struct.pack('<H', 1))

        num_records = 3
        f.write(struct.pack('<I', num_records))

        f.write(struct.pack('<Q I h B', 1620000000, 101, 2350, 1))

        f.write(struct.pack('<Q I h B', 1620000060, 102, 1850, 0))

        f.write(struct.pack('<Q I h B', 1620000120, 103, -350, 1))

    print(f"Файл {filepath} успешно создан с {num_records} записями.")

if __name__ == '__main__':
    create_data_bin('data.bin')