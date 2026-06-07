import socket
import threading
import os
from task_2 import encrypt_file
from task_4 import validate_json
from task_5 import validate_xml

BASE_DIR = 'resource'
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def recv_exact(conn, n):
    data = b''
    while len(data) < n:
        chunk = conn.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    try:
        conn.settimeout(10)
        while True:
            header = recv_exact(conn, 6)
            if header is None:
                break
            cmd = header[:4].decode()
            name_len = int.from_bytes(header[4:6], 'little')
            name_bytes = recv_exact(conn, name_len)
            if name_bytes is None:
                break
            name = name_bytes.decode()
            print(f"[DEBUG] Команда: {cmd}, имя: {name}")

            if cmd == 'UPLD':
                data_len_bytes = recv_exact(conn, 4)
                if data_len_bytes is None:
                    break
                data_len = int.from_bytes(data_len_bytes, 'little')
                data = recv_exact(conn, data_len)
                if data is None:
                    break
                filepath = os.path.join(UPLOAD_DIR, name)
                with open(filepath, 'wb') as f:
                    f.write(data)
                valid = False
                if name.endswith('.json'):
                    valid = validate_json(data.decode('utf-8'))
                elif name.endswith('.xml'):
                    valid = validate_xml(data.decode('utf-8'))
                if valid:
                    bin_name = os.path.splitext(name)[0] + '.bin'
                    bin_path = os.path.join(UPLOAD_DIR, bin_name)
                    encrypt_file(filepath, bin_path, key=0xAA)
                    conn.sendall(b'OK')
                else:
                    conn.sendall(b'INVALID')
            elif cmd == 'DOWN':
                bin_path = os.path.join(UPLOAD_DIR, name)
                print(f"[DEBUG] Ищем файл: {bin_path}")
                if not os.path.exists(bin_path):
                    print("[DEBUG] Файл не найден, отправляем NOFILE")
                    conn.sendall(b'NOFILE')
                    continue
                with open(bin_path, 'rb') as f:
                    content = f.read()
                print(f"[DEBUG] Отправляем {len(content)} байт")
                conn.sendall(len(content).to_bytes(4, 'little') + content)
            else:
                conn.sendall(b'ERROR')
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()
        print(f"Disconnected {addr}")

def main():
    HOST = '127.0.0.1'
    PORT = 5555
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        print(f"Upload directory: {UPLOAD_DIR}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == '__main__':
    main()