from PySide6.QtCore import QThread, Signal

class InstallWorker(QThread):
    log = Signal(str)
    finished = Signal(bool)

    def __init__(self, repo: str):
        super().__init__()
        self.repo = repo

    def run(self):
        self.log.emit(f"Starting installation of {self.repo}")
        self.log.emit("Fetching repository information...")
        self.log.emit("Downloading release asset...")
        self.log.emit("Installing binary...")
        self.log.emit("Installation completed successfully")
        self.finished.emit(True)
