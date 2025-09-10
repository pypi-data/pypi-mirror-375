"""
Model weight management for TextOverlay package.
Downloads and caches model weights on first use.
"""

import os
import hashlib
import requests
from pathlib import Path
from typing import Optional
import torch


class ModelDownloader:
    """Handles downloading and caching of model weights."""

    # Model configurations (official Google Drive links from U^2-Net repo)
    MODELS = {
        'u2net': {
            'url': 'https://drive.google.com/uc?id=1ao1ovG1Qtx4b7EoskHXmi2E9rp5CHLcZ',
            'filename': 'u2net.pth',
            'sha256': None,  # Replace with actual hash if you want verification
            'size_mb': 176
        },
        'u2netp': {
            'url': 'https://drive.google.com/uc?id=1rbSTGKAE-MTxBYHd-51l2hMOQPT_7EPy',
            'filename': 'u2netp.pth',
            'sha256': None,
            'size_mb': 4.7
        }
    }

    def __init__(self):
        # Get package directory and create checkpoints folder
        package_dir = Path(__file__).parent
        self.checkpoint_dir = package_dir / 'checkpoints'
        self.checkpoint_dir.mkdir(exist_ok=True)

    def get_model_path(self, model_name: str) -> Path:
        """Get the local path for a model."""
        if model_name not in self.MODELS:
            raise ValueError(f"Unknown model: {model_name}. Available: {list(self.MODELS.keys())}")

        filename = self.MODELS[model_name]['filename']
        return self.checkpoint_dir / filename

    def is_model_available(self, model_name: str) -> bool:
        """Check if model weights are already downloaded."""
        return self.get_model_path(model_name).exists()

    def verify_model(self, model_name: str) -> bool:
        """Verify model integrity using SHA256 hash (if provided)."""
        model_path = self.get_model_path(model_name)
        if not model_path.exists():
            return False

        expected_hash = self.MODELS[model_name]['sha256']
        if not expected_hash:
            return True  # skip if no hash available

        sha256_hash = hashlib.sha256()
        with open(model_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)

        actual_hash = sha256_hash.hexdigest()
        return actual_hash == expected_hash

    def download_model(self, model_name: str, force_redownload: bool = False) -> Path:
        """
        Download model weights if not already available.
        """
        if model_name not in self.MODELS:
            raise ValueError(f"Unknown model: {model_name}")

        model_config = self.MODELS[model_name]
        model_path = self.get_model_path(model_name)

        # Check if we need to download
        if not force_redownload and model_path.exists():
            if self.verify_model(model_name):
                print(f"✅ Model {model_name} already available at {model_path}")
                return model_path
            else:
                print(f"⚠️  Model {model_name} failed verification, re-downloading...")

        print(f"📥 Downloading {model_name} model ({model_config['size_mb']}MB)...")
        print(f"   Source: {model_config['url']}")

        try:
            # Stream download
            response = requests.get(model_config['url'], stream=True, allow_redirects=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(model_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r   Progress: {progress:.1f}%", end='', flush=True)
                        else:
                            mb_downloaded = downloaded / (1024 * 1024)
                            print(f"\r   Downloaded: {mb_downloaded:.1f}MB", end='', flush=True)

            print(f"\n✅ Downloaded {model_name} to {model_path}")

            if not self.verify_model(model_name):
                print(f"⚠️  Warning: Downloaded model failed verification (no hash or mismatch)")

            return model_path

        except Exception as e:
            if model_path.exists():
                model_path.unlink()  # clean up
            raise RuntimeError(f"Failed to download {model_name}: {e}")

    def list_available_models(self):
        """List all available models and their status."""
        print("📋 Available Models:")
        print("-" * 50)
        for model_name, config in self.MODELS.items():
            status = "✅ Downloaded" if self.is_model_available(model_name) else "📥 Not downloaded"
            print(f"  {model_name:10} | {config['size_mb']:6.1f}MB | {status}")

    def clean_cache(self, model_name: Optional[str] = None):
        """Remove downloaded model weights."""
        if model_name:
            if model_name not in self.MODELS:
                print(f"Unknown model: {model_name}")
                return

            model_path = self.get_model_path(model_name)
            if model_path.exists():
                model_path.unlink()
                print(f"🗑️  Removed {model_name} weights")
            else:
                print(f"Model {model_name} was not downloaded")
        else:
            for model_file in self.checkpoint_dir.glob("*.pth"):
                model_file.unlink()
                print(f"🗑️  Removed {model_file.name}")


# Singleton instance
_downloader = None

def get_downloader() -> ModelDownloader:
    global _downloader
    if _downloader is None:
        _downloader = ModelDownloader()
    return _downloader

def ensure_model_available(model_name: str = 'u2net') -> Path:
    downloader = get_downloader()
    return downloader.download_model(model_name)

def load_u2net_model(model_name: str = 'u2net'):
    """Load U2Net model, downloading weights if necessary."""
    model_path = ensure_model_available(model_name)

    from .u2net import U2NET, U2NETP  # Adjust if needed

    if model_name == 'u2net':
        model = U2NET(3, 1)
    elif model_name == 'u2netp':
        model = U2NETP(3, 1)
    else:
        raise ValueError(f"Unknown model type: {model_name}")

    if torch.cuda.is_available():
        model.load_state_dict(torch.load(model_path))
        model.cuda()
    else:
        model.load_state_dict(torch.load(model_path, map_location='cpu'))

    model.eval()
    print(f"✅ Successfully loaded {model_name} model from {model_path}")
    return model


# CLI interface
def main():
    import argparse
    parser = argparse.ArgumentParser(description='TextOverlay Model Manager')
    parser.add_argument('command', choices=['list', 'download', 'clean'], help='Command to execute')
    parser.add_argument('--model', default='u2net', help='Model name (u2net or u2netp)')
    parser.add_argument('--force', action='store_true', help='Force redownload')

    args = parser.parse_args()
    downloader = get_downloader()

    if args.command == 'list':
        downloader.list_available_models()
    elif args.command == 'download':
        downloader.download_model(args.model, args.force)
    elif args.command == 'clean':
        downloader.clean_cache(args.model)


if __name__ == '__main__':
    main()
