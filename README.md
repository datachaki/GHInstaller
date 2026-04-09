# GHInstaller

A Python GUI application for browsing and downloading release assets from GitHub repositories.

## Features

- Browse GitHub repositories by owner/name (e.g., `sharkdp/bat`)
- View repository information (stars, license, owner)
- Browse all releases and their assets
- Download release assets with progress tracking
- Real-time log output

## Requirements

- Python 3.10+
- PySide6
- requests

## Installation

1. Clone or download this repository:
   ```bash
   git clone https://github.com/datachaki/GHInstaller
   cd ghinstaller
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python main.py
```

### How to Use

1. Enter a GitHub repository in the format `owner/repo` (e.g., `sharkdp/bat`)
2. Click **Fetch repository info** to load repository details and releases
3. Select a release from the list to view its available assets
4. Click on an asset to download it to the current directory
5. Monitor download progress and logs in the output panel

## Project Structure

```
ghinstaller/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── core/
│   ├── github_client.py    # GitHub API client (fetch repo info & releases)
│   ├── download_worker.py  # Handles file downloads with progress
│   └── install_worker.py   # Worker for installation tasks
└── gui/
    └── main_window.py      # Main application window
```

## Components

### `core/github_client.py`
- `fetch_repository_info(full_name)` - Fetches repository metadata (stars, license, owner)
- `fetch_repository_releases(full_name)` - Fetches all releases with their assets

### `core/download_worker.py`
- `DownloadWorker` - Qt worker that handles downloads in a background thread with progress reporting

### `core/install_worker.py`
- `InstallWorker` - Qt worker for handling installation tasks with log output

### `gui/main_window.py`
- `MainWindow` - The main application window with all UI components and event handlers

## License

MIT
