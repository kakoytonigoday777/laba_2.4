import socket
import sys
import os

BASE_DIR = 'resource'

def resolve_path(filename):
    if os.path.sep in filename or (os.path.altsep and os.path.altsep in filename):
        return filename
    return os.path.join(BASE_DIR, filename)

def upload_file(host, port, filepath):
    full_path = resolve_path(filepath)
    if not os.path.exists(full_path):
        print(f"Файл {full_path} не найден")
        return
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(10)
            sock.connect((host, port))
            filename = os.path.basename(full_path)
            with open(full_path, 'rb') as f:
                data = f.read()
            cmd = b'UPLD'
            name_enc = filename.encode()
            name_len = len(name_enc).to_bytes(2, 'little')
            data_len = len(data).to_bytes(4, 'little')
            sock.send(cmd + name_len + name_enc + data_len + data)
            response = sock.recv(1024)
            print("Server response:", response.decode())
    except socket.timeout:
        print("Timeout: сервер не ответил")
    except ConnectionRefusedError:
        print("Не удалось подключиться к серверу. Запустите сервер.")
    except Exception as e:
        print(f"Ошибка: {e}")

def download_file(host, port, remote_name, local_path):
    full_local = resolve_path(local_path)
    local_dir = os.path.dirname(full_local)
    if local_dir and not os.path.exists(local_dir):
        os.makedirs(local_dir)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(10)
            sock.connect((host, port))
            cmd = b'DOWN'
            name_enc = remote_name.encode()
            name_len = len(name_enc).to_bytes(2, 'little')
            sock.send(cmd + name_len + name_enc)

            header = sock.recv(4)
            if not header:
                print("Нет ответа от сервера")
                return
            if header == b'NOFI':
                rest = sock.recv(2)
                error_msg = header + rest
                print("Server error:", error_msg.decode())
                return
            data_len = int.from_bytes(header, 'little')
            data = b''
            while len(data) < data_len:
                chunk = sock.recv(min(4096, data_len - len(data)))
                if not chunk:
                    break
                data += chunk
            with open(full_local, 'wb') as f:
                f.write(data)
            print(f"Downloaded {data_len} bytes to {full_local}")
    except socket.timeout:
        print("Timeout: сервер не ответил")
    except ConnectionRefusedError:
        print("Не удалось подключиться к серверу. Запустите сервер.")
    except Exception as e:
        print(f"Ошибка: {e}")

def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python task_6_client.py upload <filepath>")
        print("  python task_6_client.py download <remote_name> <local_path>")
        sys.exit(1)

    cmd = sys.argv[1]
    host, port = '127.0.0.1', 5555

    if cmd == 'upload':
        if len(sys.argv) != 3:
            print("For upload: python task_6_client.py upload <filepath>")
            sys.exit(1)
        upload_file(host, port, sys.argv[2])
    elif cmd == 'download':
        if len(sys.argv) != 4:
            print("For download: python task_6_client.py download <remote_name> <local_path>")
            sys.exit(1)
        download_file(host, port, sys.argv[2], sys.argv[3])
    else:
        print("Unknown command. Use 'upload' or 'download'.")
        sys.exit(1)

if __name__ == '__main__':
    main()