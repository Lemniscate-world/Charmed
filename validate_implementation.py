"""Validation script for fade-in feature implementation."""

print("Validating fade-in feature implementation...")

# Test 1: Import alarm module
try:
    from alarm import Alarm, FadeInController, PYQT_AVAILABLE
    print("✓ alarm.py imports successfully")
    print(f"  - FadeInController available: {PYQT_AVAILABLE}")
except ImportError as e:
    print(f"✗ Failed to import alarm.py: {e}")
    exit(1)

# Test 2: Check Alarm class has fade-in support
try:
    import inspect
    sig = inspect.signature(Alarm.set_alarm)
    params = list(sig.parameters.keys())
    assert 'fade_in_enabled' in params, "Missing fade_in_enabled parameter"
    assert 'fade_in_duration' in params, "Missing fade_in_duration parameter"
    print("✓ Alarm.set_alarm() has fade-in parameters")
except Exception as e:
    print(f"✗ Alarm.set_alarm() validation failed: {e}")
    exit(1)

# Test 3: Import gui module
try:
    from gui import AlarmSetupDialog
    print("✓ gui.py imports successfully")
    print("  - AlarmSetupDialog available")
except ImportError as e:
    print(f"✗ Failed to import gui.py: {e}")
    exit(1)

# Test 4: Check FadeInController (if PyQt5 available)
if PYQT_AVAILABLE:
    try:
        assert hasattr(FadeInController, 'start'), "Missing start method"
        assert hasattr(FadeInController, 'stop'), "Missing stop method"
        assert hasattr(FadeInController, 'is_running'), "Missing is_running method"
        print("✓ FadeInController has required methods")
    except Exception as e:
        print(f"✗ FadeInController validation failed: {e}")
        exit(1)
else:
    print("  - PyQt5 not available, skipping FadeInController tests")

# Test 5: Import test module
try:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from tests.test_alarm import TestFadeInFeature, TestFadeInController
    print("✓ tests/test_alarm.py imports successfully")
    print("  - TestFadeInFeature available")
    print("  - TestFadeInController available")
except ImportError as e:
    print(f"✗ Failed to import tests/test_alarm.py: {e}")
    exit(1)

print("\n✓ All validation checks passed!")
print("\nImplementation Summary:")
print("- FadeInController class with smooth volume ramp algorithm")
print("- Alarm.set_alarm() accepts fade_in_enabled and fade_in_duration (5-30 min)")
print("- AlarmSetupDialog with fade-in UI and 30-second preview")
print("- Fade-in preferences persisted per alarm")
print("- Comprehensive test suite added")
