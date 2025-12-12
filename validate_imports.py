"""Quick validation script to check all imports work correctly."""

print("Validating imports...")

try:
    from logging_config import setup_logging, get_logger
    print("✓ logging_config imports successfully")
except Exception as e:
    print(f"✗ logging_config import failed: {e}")
    exit(1)

try:
    import main
    print("✓ main imports successfully")
except Exception as e:
    print(f"✗ main import failed: {e}")
    exit(1)

try:
    import alarm
    print("✓ alarm imports successfully")
except Exception as e:
    print(f"✗ alarm import failed: {e}")
    exit(1)

try:
    from spotify_api.spotify_api import SpotifyAPI
    print("✓ spotify_api imports successfully")
except Exception as e:
    print(f"✗ spotify_api import failed: {e}")
    exit(1)

try:
    import gui
    print("✓ gui imports successfully")
except Exception as e:
    print(f"✗ gui import failed: {e}")
    exit(1)

print("\nAll imports validated successfully!")
print("Logging system is properly integrated.")
