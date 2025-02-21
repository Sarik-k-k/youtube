import os
import sys
from pathlib import Path

def verify_paths():
    """Verify all download paths are correct and writable"""
    root_dir = Path(__file__).parent.parent
    download_dir = root_dir / 'downloads'
    
    required_dirs = {
        'base': download_dir,
        'videos': download_dir / 'videos',
        'audio': download_dir / 'audio',
        'temp': download_dir / 'temp',
        'playlists': download_dir / 'playlists'
    }
    
    for name, path in required_dirs.items():
        try:
            path.mkdir(parents=True, exist_ok=True)
            # Test write permissions
            test_file = path / '.write_test'
            test_file.write_text('test')
            test_file.unlink()
            print(f'✓ {name}: {path} (writable)')
        except Exception as e:
            print(f'✗ {name}: {path}')
            print(f'  Error: {str(e)}')
            sys.exit(1)

if __name__ == '__main__':
    verify_paths()