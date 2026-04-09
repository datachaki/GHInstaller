import requests

BASE_URL = "https://api.github.com/repos"

def fetch_repository_info(full_name: str) -> dict:
    response = requests.get(f"{BASE_URL}/{full_name}")
    response.raise_for_status()
    data = response.json()

    return {
        "full_name": data["full_name"],
        "owner": data["owner"]["login"],
        "stars": data["stargazers_count"],
        "license": data["license"]["name"] if data["license"] else "None",
        "html_url": data["html_url"]
    }

def fetch_repository_releases(full_name: str) -> list[dict]:
    """Fetches releases of a GitHub repository."""
    url = f"https://api.github.com/repos/{full_name}/releases"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()  # lista releases

    releases = []
    for release in data:
        releases.append({
            "tag_name": release["tag_name"],
            "name": release["name"],
            "assets": [
                {
                    "name": asset["name"],
                    "download_url": asset["browser_download_url"]
                }
                for asset in release.get("assets", [])
            ],
            "html_url": release["html_url"]
        })

    return releases
