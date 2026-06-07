def rotate_left(byte, bits=2):
    bits %= 8
    return ((byte << bits) | (byte >> (8 - bits))) & 0xFF

def rotate_right(byte, bits=2):
    bits %= 8
    return ((byte >> bits) | ((byte & ((1 << bits) - 1)) << (8 - bits))) & 0xFF

def encrypt_file(input_file, output_file, key):
    with open(input_file, 'rb') as fin, open(output_file, 'wb') as fout:
        while True:
            chunk = fin.read(4096)
            if not chunk:
                break
            encrypted = bytes(rotate_left(b, 2) ^ key for b in chunk)
            fout.write(encrypted)

def decrypt_file(input_file, output_file, key):
    with open(input_file, 'rb') as fin, open(output_file, 'wb') as fout:
        while True:
            chunk = fin.read(4096)
            if not chunk:
                break
            decrypted = bytes(rotate_right(b ^ key, 2) for b in chunk)
            fout.write(decrypted)

if __name__ == '__main__':
    key = 0xAA

    with open('resource/plain.bin', 'wb') as f:
        f.write(b'Hello, world! This is a test file for encryption.')
    encrypt_file('resource/plain.bin', 'resource/encrypted.bin', key)
    decrypt_file('resource/encrypted.bin', 'resource/decrypted.bin', key)
    print("Шифрование и дешифрование выполнены. Проверьте файлы plain.bin и decrypted.bin")