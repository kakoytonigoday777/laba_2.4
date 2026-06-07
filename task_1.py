import struct

def parse_binary_file(filepath):
    with open(filepath, 'rb') as f:
        signature = f.read(4)
        if signature != b'DATA':
            raise ValueError("Неверная сигнатура файла")
        version = struct.unpack('<H', f.read(2))[0]
        num_records = struct.unpack('<I', f.read(4))[0]

        total_temp = 0.0
        active_flags = 0

        for _ in range(num_records):
            data = f.read(15)
            if len(data) < 15:
                break
            timestamp, record_id, temp_raw, flag = struct.unpack('<Q I h B', data)
            temperature = temp_raw / 100.0
            total_temp += temperature
            if flag != 0:
                active_flags += 1

        avg_temp = total_temp / num_records if num_records > 0 else 0
        print(f"Версия файла: {version}")
        print(f"Количество записей: {num_records}")
        print(f"Средняя температура: {avg_temp:.2f} °C")
        print(f"Количество активных флагов: {active_flags}")

if __name__ == '__main__':
    parse_binary_file('resource/data.bin')