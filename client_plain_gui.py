import sys
import socket
import platform
import subprocess
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit, QFileDialog, QLabel, QInputDialog, QProgressBar
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
        self.delete_btn = QPushButton("Dosya Sil")
        self.exit_btn = QPushButton("Çıkış")

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.hide()

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.log)
        layout.addWidget(self.upload_btn)
        layout.addWidget(self.download_btn)
        layout.addWidget(self.list_btn)
        layout.addWidget(self.delete_btn)
        layout.addWidget(self.exit_btn)
        layout.addWidget(self.progress)
        self.setLayout(layout)

        self.upload_btn.clicked.connect(self.upload_file)
        self.download_btn.clicked.connect(self.download_file)
        self.list_btn.clicked.connect(self.list_files)
        self.exit_btn.clicked.connect(self.close_connection)
        self.delete_btn.clicked.connect(self.delete_file)

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect(("127.0.0.1", 5000))
            self.label.setText("Bağlantı başarılı")
        except Exception as e:
            self.label.setText("Bağlantı başarısız")
            self.log.append(str(e))

        self.setStyleSheet("""
            QWidget {
                background-color: #f2f2f2;
                font-family: Segoe UI, sans-serif;
                font-size: 13px;
            }

            QPushButton {
                background-color: #FF9800;
                color: white;
                border-radius: 6px;
                padding: 8px;
            }

            QPushButton:hover {
                background-color: #45a049;
            }

            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                padding: 5px;
            }

            QProgressBar {
                border: 1px solid #bbb;
                border-radius: 5px;
                text-align: center;
            }

            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 20px;
            }

            QLabel {
                font-weight: bold;
            }
        """)

    def upload_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Dosya Seç")
        if not path:
            return
        filename = os.path.basename(path)
        self.s.sendall(f"UPLOAD {filename}".encode())
        with open(path, "rb") as f:
            data = f.read()
        self.s.sendall(len(data).to_bytes(8, 'big'))

        self.progress.setValue(0)
        self.progress.show()

        sent = 0
        chunk_size = 4096
        while sent < len(data):
            chunk = data[sent:sent + chunk_size]
            self.s.sendall(chunk)
            sent += len(chunk)
            progress = int((sent / len(data)) * 100)
            self.progress.setValue(progress)

        size_kb = len(data) / 1024
        self.log.append(f"✅ {filename} yüklendi ({size_kb:.1f} KB)")
        self.progress.hide()

    def download_file(self):
        self.s.sendall(b"LIST")
        files = self.s.recv(2048).decode().split(",")
        file, ok = QInputDialog.getItem(self, "Dosya Seç", "İndirilecek dosya:", files, 0, False)
        if not ok:
            return
        self.s.sendall(f"DOWNLOAD {file}".encode())
        size = int.from_bytes(self.s.recv(8), 'big')

        self.progress.setValue(0)
        self.progress.show()

        data = b""

        received = 0
        chunk_size = 4096
        while received < size:
            chunk = self.s.recv(min(chunk_size, size - received))
            if not chunk:
                break
            data += chunk
            received += len(chunk)
            progress = int((received / size) * 100)
            self.progress.setValue(progress)

        self.progress.hide()

        save_path, _ = QFileDialog.getSaveFileName(self, "Kaydet", "indirilen_" + file)
        if not save_path:
            self.log.append("İndirme iptal edildi.")
            return


        with open(save_path, "wb") as f:
            f.write(data)
        size_kb = len(data) / 1024
        self.log.append(f"✅ {file} indirildi ({size_kb:.1f} KB) → {save_path}")

        try:
            if platform.system() == "Windows":
                os.startfile(save_path)
            elif platform.system() == "Darwin":
                subprocess.call(["open", save_path])
            else:
                subprocess.call(["xdg-open", save_path])
        except Exception as e:
            self.log.append(f"⚠️ Dosya açılırken hata: {e}")


    def list_files(self):
        self.s.sendall(b"LIST")
        files = self.s.recv(2048).decode()
        self.log.append("📂 Sunucudaki dosyalar:\n" + files)

    def delete_file(self):
        self.s.sendall(b"LIST")
        files = self.s.recv(2048).decode().split(",")
        if not files or files == ['']:
            self.log.append("⚠️ Sunucuda silinecek dosya yok.")
            return
        file, ok = QInputDialog.getItem(self, "Dosya Seç", "Silinecek dosya:", files, 0, False)
        if not ok:
            return
        self.s.sendall(f"DELETE {file}".encode())
        response = self.s.recv(1024).decode()
        if response == "OK":
            self.log.append(f"🗑️ {file} başarıyla silindi")
        else:
            self.log.append(f"❌ Silinemedi: {response}")

    def close_connection(self):
        self.s.sendall(b"EXIT")
        self.s.close()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = PlainClient()
    gui.show()
    sys.exit(app.exec_())
