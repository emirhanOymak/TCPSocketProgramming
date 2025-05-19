import sys
import socket
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit, QFileDialog, QLabel, QInputDialog
)

class PlainClient(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dosya İstemcisi")
        self.resize(500, 400)

        self.log = QTextEdit()
        self.log.setReadOnly(True)

        self.label = QLabel("Sunucuya bağlanılıyor...")

        self.upload_btn = QPushButton("Dosya Yükle")
        self.download_btn = QPushButton("Dosya İndir")
        self.list_btn = QPushButton("Dosya Listele")
        self.exit_btn = QPushButton("Çıkış")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.log)
        layout.addWidget(self.upload_btn)
        layout.addWidget(self.download_btn)
        layout.addWidget(self.list_btn)
        layout.addWidget(self.exit_btn)
        self.setLayout(layout)

        self.upload_btn.clicked.connect(self.upload_file)
        self.download_btn.clicked.connect(self.download_file)
        self.list_btn.clicked.connect(self.list_files)
        self.exit_btn.clicked.connect(self.close_connection)

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect(("127.0.0.1", 5000))
            self.label.setText("Bağlantı başarılı")
        except Exception as e:
            self.label.setText("Bağlantı başarısız")
            self.log.append(str(e))

    def upload_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Dosya Seç")
        if not path:
            return
        filename = os.path.basename(path)
        self.s.sendall(f"UPLOAD {filename}".encode())
        with open(path, "rb") as f:
            data = f.read()
        self.s.sendall(len(data).to_bytes(8, 'big'))
        self.s.sendall(data)
        self.log.append(f"✅ {filename} yüklendi")

    def download_file(self):
        self.s.sendall(b"LIST")
        files = self.s.recv(2048).decode().split(",")
        file, ok = QInputDialog.getItem(self, "Dosya Seç", "İndirilecek dosya:", files, 0, False)
        if not ok:
            return
        self.s.sendall(f"DOWNLOAD {file}".encode())
        size = int.from_bytes(self.s.recv(8), 'big')
        data = b""
        while len(data) < size:
            data += self.s.recv(min(4096, size - len(data)))
        with open("indirilen_" + file, "wb") as f:
            f.write(data)
        self.log.append(f"✅ {file} indirildi")

    def list_files(self):
        self.s.sendall(b"LIST")
        files = self.s.recv(2048).decode()
        self.log.append("📂 Sunucudaki dosyalar:\n" + files)

    def close_connection(self):
        self.s.sendall(b"EXIT")
        self.s.close()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = PlainClient()
    gui.show()
    sys.exit(app.exec_())
