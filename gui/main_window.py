from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTextEdit, QLabel, QListWidget, QProgressBar,
    QFileDialog, QComboBox
)
from core.github_client import fetch_repository_info, fetch_repository_releases
from core.download_worker import DownloadWorker
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GHInstaller")
        self.resize(800, 600)

        central_widget = QWidget()
        layout = QVBoxLayout()

        # Repo input
        self.repo_input = QLineEdit()
        self.repo_input.setPlaceholderText("owner/repo (e.g. sharkdp/bat)")

        # Fetch button
        self.fetch_button = QPushButton("Fetch repository info")
        self.fetch_button.clicked.connect(self.on_fetch_clicked)

        # Install button (disabled for now)
        self.install_button = QPushButton("Install")
        self.install_button.setEnabled(False)

        # Repository info label
        self.repo_info_label = QLabel("Repository: —")

        # Releases list
        self.releases_list = QListWidget()
        self.releases_list.addItem("Releases will appear here...")
        self.releases_list.itemClicked.connect(self.on_release_clicked)

        # Assets list with download button
        self.assets_list = QListWidget()
        self.assets_list.addItem("Assets will appear here...")
        self.assets_list.itemClicked.connect(self.on_asset_clicked)

        # Download button row
        self.download_button = QPushButton("Download Selected Asset")
        self.download_button.setEnabled(False)
        self.download_button.clicked.connect(self.on_download_clicked)

        # Selected asset storage
        self.selected_asset = None

        # Save directory selector
        dir_layout = QHBoxLayout()
        self.save_dir_input = QLineEdit()
        self.save_dir_input.setPlaceholderText("Save directory")
        self.save_dir_input.setText(os.getcwd())
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.on_browse_clicked)
        dir_layout.addWidget(QLabel("Save to:"))
        dir_layout.addWidget(self.save_dir_input)
        dir_layout.addWidget(self.browse_button)

        self.dir_widget = QWidget()
        self.dir_widget.setLayout(dir_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        # Log output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Logs will appear here...")

        # Add widgets to layout
        layout.addWidget(self.repo_input)
        layout.addWidget(self.fetch_button)
        layout.addWidget(self.repo_info_label)
        layout.addWidget(self.install_button)
        layout.addWidget(self.releases_list)
        layout.addWidget(self.assets_list)
        layout.addWidget(self.download_button)
        layout.addWidget(self.dir_widget)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.log_output)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    # Log helper
    def log(self, message: str):
        self.log_output.append(message)

    # Fetch repository info + releases
    def on_fetch_clicked(self):
        repo = self.repo_input.text().strip()

        if "/" not in repo:
            self.log("Invalid repository format. Use owner/repo")
            return

        self.log(f"Fetching repository info for {repo}...")

        try:
            # Fetch repo info
            info = fetch_repository_info(repo)
            self.repo_info_label.setText(
                f"Repository: {info['full_name']} | "
                f"Owner: {info['owner']} | "
                f"⭐ {info['stars']} | "
                f"License: {info['license']}"
            )

            # Fetch releases
            releases = fetch_repository_releases(repo)
            self.releases_list.clear()
            if not releases:
                self.releases_list.addItem("No releases found.")
            else:
                for release in releases:
                    self.releases_list.addItem(f"{release['tag_name']}: {release['name']}")
            self.log(f"{len(releases)} releases fetched.")
            self.install_button.setEnabled(True)

        except Exception as e:
            self.log(f"Error fetching repository: {e}")
            self.install_button.setEnabled(False)

    # When a release is clicked, show its assets
    def on_release_clicked(self, item):
        selected_text = item.text()
        tag_name = selected_text.split(":")[0].strip()

        try:
            releases = fetch_repository_releases(self.repo_input.text().strip())
            self.assets_list.clear()
            release_found = False
            for release in releases:
                if release["tag_name"] == tag_name:
                    release_found = True
                    assets = release.get("assets", [])
                    if not assets:
                        self.assets_list.addItem("No assets found for this release.")
                    else:
                        for asset in assets:
                            self.assets_list.addItem(f"{asset['name']} | {asset['download_url']}")
                    break
            if not release_found:
                self.assets_list.addItem("Release not found.")
        except Exception as e:
            self.log(f"Error fetching assets: {e}")

    # When an asset is clicked, select it for download
    def on_asset_clicked(self, item):
        parts = item.text().split("|")
        if len(parts) != 2:
            self.log("Invalid asset format.")
            self.selected_asset = None
            self.download_button.setEnabled(False)
            return

        asset_name = parts[0].strip()
        url = parts[1].strip()
        self.selected_asset = {"name": asset_name, "url": url}
        self.download_button.setEnabled(True)
        self.log(f"Selected asset: {asset_name}")

    # Browse for save directory
    def on_browse_clicked(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Save Directory",
            self.save_dir_input.text()
        )
        if directory:
            self.save_dir_input.setText(directory)

    # Download the selected asset
    def on_download_clicked(self):
        if not self.selected_asset:
            self.log("No asset selected.")
            return

        save_dir = self.save_dir_input.text().strip()
        if not save_dir:
            save_dir = os.getcwd()

        save_path = os.path.join(save_dir, self.selected_asset["name"])
        self.log(f"Starting download: {self.selected_asset['name']}")
        self.log(f"Save path: {save_path}")

        # Create and start worker thread
        self.worker = DownloadWorker(self.selected_asset["url"], save_path)

        # Connect signals
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self._on_download_finished)
        self.worker.error.connect(lambda e: self.log(f"Download error: {e}"))

        # Start download
        self.worker.start()

    def _on_download_finished(self, msg):
        self.log(msg)
        self.worker.quit()
        self.worker.wait()
        self.worker.deleteLater()
