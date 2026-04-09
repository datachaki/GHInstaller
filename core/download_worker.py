import requests
from PySide6.QtCore import QThread, Signal

class DownloadWorker(QThread):
    progress = Signal(int)      # percent
    finished = Signal(str)      # message
    error = Signal(str)

    def __init__(self, url: str, save_path: str):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.setObjectName("DownloadWorker")

    def run(self):
        try:
            with requests.get(self.url, stream=True) as r:
                r.raise_for_status()
                total_length = r.headers.get('content-length')
                if total_length is None:
                    total_length = 0
                else:
                    total_length = int(total_length)

                downloaded = 0
                with open(self.save_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_length:
                                percent = int(downloaded / total_length * 100)
                                self.progress.emit(percent)

            self.finished.emit(f"Downloaded: {self.save_path}")

        except Exception as e:
            self.error.emit(str(e))
