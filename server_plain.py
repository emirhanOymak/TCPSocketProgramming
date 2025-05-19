import socket
import threading
import os

HOST = '0.0.0.0'
PORT = 5000

def handle_client(conn, addr):
    print(f" Yeni Bağlantı: {addr}")
    try:
        while True:
            command = conn.recv(1024).decode()
            if not command:
                break

            if command == 'EXIT':
                break
            elif command == 'LIST':
                files = ",".join(os.listdir("shared"))
                conn.sendall(files.encode())
            elif command.startswith("UPLOAD"):
                _, filename = command.split()
                filesize = int.from_bytes(conn.recv(8), 'big')
                data = b""
                while len(data) < filesize:
                    data += conn.recv(min(4096, filesize - len(data)))
                with open(os.path.join("shared", filename), "wb") as f:
                    f.write(data)
            elif command.startswith("DOWNLOAD"):
                _, filename = command.split()
                with open(os.path.join("shared", filename), "rb") as f:
                    file_data = f.read()
                conn.sendall(len(file_data).to_bytes(8, 'big'))
                conn.sendall(file_data)
            elif command.startswith("DELETE"):
                _, filename = command.split()
                try:
                    os.remove(os.path.join("shared", filename))
                    conn.sendall(b"OK")
                except Exception as e:
                    conn.sendall(f"ERROR: {e}".encode())

    finally:
        conn.close()
        print(f" Bağlantı kapandı: {addr}")

if __name__ == "__main__":
    os.makedirs("shared", exist_ok=True)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f" Sunucu Başlatıldı {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
