from artifactory import ArtifactoryPath
from pathlib import Path
import xgboost as xgb
import os


def download_from_artifactory(artifactory_url: str, repo_path: str, local_path: Path):
    """
    Download a file from Artifactory using username/password or token.
    """
    user = os.environ["ARTIFACTORY_USER"]
    password = os.environ["ARTIFACTORY_PASS"]

    full_url = f"{artifactory_url.rstrip('/')}/{repo_path.lstrip('/')}"
    remote = ArtifactoryPath(full_url, auth=(user, password))

    # Using two separate context managers (cleaner than one line)
    with remote.open("rb") as remote_file:
        data = remote_file.read()

    local_path.write_bytes(data)
    return local_path


def load_xgb_classifier(path: Path) -> xgb.XGBClassifier:
    model = xgb.XGBClassifier()
    model.load_model(str(path))
    return model


if __name__ == "__main__":
    ARTIFACTORY_URL = "https://yourcompany.jfrog.io/artifactory"
    REPO_PATH = "models-local/credit/xgb_model/1.0.0/model.json"

    LOCAL_MODEL = Path("downloaded_model.json")

    print("Downloading model...")
    download_from_artifactory(ARTIFACTORY_URL, REPO_PATH, LOCAL_MODEL)

    print("Loading model...")
    model = load_xgb_classifier(LOCAL_MODEL)

    print("Model loaded successfully!")
