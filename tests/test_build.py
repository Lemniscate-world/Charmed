"""
test_build.py - Build verification tests

These tests verify that the built executable meets quality standards.
Can be run against the compiled executable to ensure it's valid.

Usage:
    pytest tests/test_build.py -v
    pytest tests/test_build.py::test_executable_exists -v
"""

import pytest
from pathlib import Path
import struct
import os
import re
import sys


# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
EXE_PATH = DIST_DIR / "Alarmify.exe"
OUTPUT_DIR = PROJECT_ROOT / "Output"


@pytest.fixture
def executable_path():
    """Provide path to the executable."""
    return EXE_PATH


class TestExecutable:
    """Test suite for built executable."""
    
    def test_executable_exists(self, executable_path):
        """Test that the executable file exists."""
        assert executable_path.exists(), f"Executable not found at {executable_path}"
    
    def test_executable_size(self, executable_path):
        """Test that executable size is reasonable (> 10 MB)."""
        if not executable_path.exists():
            pytest.skip("Executable not built yet")
        
        size_mb = executable_path.stat().st_size / (1024 * 1024)
        assert size_mb > 10, f"Executable too small: {size_mb:.2f} MB"
        assert size_mb < 500, f"Executable too large: {size_mb:.2f} MB"
    
    def test_pe_header_valid(self, executable_path):
        """Test that executable has valid PE (Portable Executable) header."""
        if not executable_path.exists():
            pytest.skip("Executable not built yet")
        
        with open(executable_path, 'rb') as f:
            # Read DOS header
            dos_header = f.read(2)
            assert dos_header == b'MZ', "Invalid DOS header (should be 'MZ')"
            
            # Read PE offset (at 0x3C)
            f.seek(0x3C)
            pe_offset = struct.unpack('<I', f.read(4))[0]
            
            # Read PE signature
            f.seek(pe_offset)
            pe_signature = f.read(4)
            assert pe_signature == b'PE\x00\x00', "Invalid PE signature"
    
    def test_executable_is_64bit(self, executable_path):
        """Test that executable is 64-bit."""
        if not executable_path.exists():
            pytest.skip("Executable not built yet")
        
        with open(executable_path, 'rb') as f:
            # Read PE offset
            f.seek(0x3C)
            pe_offset = struct.unpack('<I', f.read(4))[0]
            
            # Read machine type from COFF header
            f.seek(pe_offset + 4)
            machine = struct.unpack('<H', f.read(2))[0]
            
            # 0x8664 = AMD64 (x64), 0x014c = I386 (x86)
            assert machine == 0x8664, f"Executable is not 64-bit (machine type: {hex(machine)})"


class TestAssets:
    """Test suite for bundled assets."""
    
    def test_dist_directory_exists(self):
        """Test that dist directory exists."""
        assert DIST_DIR.exists(), "dist directory not found"
    
    @pytest.mark.skipif(not EXE_PATH.exists(), reason="Executable not built")
    def test_no_debug_files(self):
        """Test that no debug files are in dist directory."""
        debug_extensions = ['.pdb', '.log', '.tmp']
        debug_files = []
        
        for ext in debug_extensions:
            debug_files.extend(DIST_DIR.glob(f'*{ext}'))
        
        assert len(debug_files) == 0, f"Found debug files: {debug_files}"


class TestVersionInfo:
    """Test suite for version information."""
    
    def test_spec_file_exists(self):
        """Test that PyInstaller spec file exists."""
        spec_file = PROJECT_ROOT / "alarmify.spec"
        assert spec_file.exists(), "alarmify.spec not found"
    
    def test_installer_script_exists(self):
        """Test that Inno Setup script exists."""
        iss_file = PROJECT_ROOT / "installer.iss"
        assert iss_file.exists(), "installer.iss not found"
    
    def test_version_consistency(self):
        """Test that version is consistent across files."""
        iss_file = PROJECT_ROOT / "installer.iss"
        
        if not iss_file.exists():
            pytest.skip("installer.iss not found")
        
        # Extract version from installer.iss
        content = iss_file.read_text(encoding='utf-8')
        match = re.search(r'#define MyAppVersion "([^"]+)"', content)
        
        assert match, "Version not found in installer.iss"
        version = match.group(1)
        
        # Validate version format (semantic versioning)
        version_pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$'
        assert re.match(version_pattern, version), f"Invalid version format: {version}"
    
    def test_version_info_in_executable(self, executable_path):
        """Test that executable includes proper version information."""
        if not executable_path.exists():
            pytest.skip("Executable not built yet")
        
        # Read the executable file to check for version info strings
        # PyInstaller embeds version info from version_info.txt
        with open(executable_path, 'rb') as f:
            content = f.read()
            
            # Check for common version info strings
            version_strings = [
                b'Alarmify',
                b'FileDescription',
                b'ProductName',
            ]
            
            for version_str in version_strings:
                assert version_str in content, f"Version string '{version_str.decode()}' not found in executable"


class TestBuildConfiguration:
    """Test suite for build configuration files."""
    
    def test_spec_file_syntax(self):
        """Test that spec file has valid Python syntax."""
        spec_file = PROJECT_ROOT / "alarmify.spec"
        
        if not spec_file.exists():
            pytest.skip("alarmify.spec not found")
        
        try:
            with open(spec_file, 'r', encoding='utf-8') as f:
                code = f.read()
                compile(code, str(spec_file), 'exec')
        except SyntaxError as e:
            pytest.fail(f"Syntax error in alarmify.spec: {e}")
    
    def test_required_assets_defined(self):
        """Test that required assets are defined in spec file."""
        spec_file = PROJECT_ROOT / "alarmify.spec"
        
        if not spec_file.exists():
            pytest.skip("alarmify.spec not found")
        
        content = spec_file.read_text(encoding='utf-8')
        
        required_assets = [
            'spotify_style.qss',
            'Logo First Draft.png',
        ]
        
        for asset in required_assets:
            assert asset in content, f"Asset '{asset}' not found in alarmify.spec"
    
    def test_spec_includes_cloud_sync_module(self):
        """Test that spec file includes cloud_sync module dependencies."""
        spec_file = PROJECT_ROOT / "alarmify.spec"
        
        if not spec_file.exists():
            pytest.skip("alarmify.spec not found")
        
        content = spec_file.read_text(encoding='utf-8')
        
        # Check for cloud_sync in hiddenimports or datas
        assert 'cloud_sync' in content, "cloud_sync module not referenced in alarmify.spec"
    
    def test_spec_includes_device_wake_manager(self):
        """Test that spec file includes device_wake_manager dependencies."""
        spec_file = PROJECT_ROOT / "alarmify.spec"
        
        if not spec_file.exists():
            pytest.skip("alarmify.spec not found")
        
        content = spec_file.read_text(encoding='utf-8')
        
        # Check for device_wake_manager
        assert 'device_wake_manager' in content, "device_wake_manager not referenced in alarmify.spec"
    
    def test_spec_includes_logging_config(self):
        """Test that spec file includes logging_config dependencies."""
        spec_file = PROJECT_ROOT / "alarmify.spec"
        
        if not spec_file.exists():
            pytest.skip("alarmify.spec not found")
        
        content = spec_file.read_text(encoding='utf-8')
        
        # Check for logging_config
        assert 'logging_config' in content, "logging_config not referenced in alarmify.spec"
    
    def test_spec_includes_all_new_dependencies(self):
        """Test that spec file includes all new module dependencies."""
        spec_file = PROJECT_ROOT / "alarmify.spec"
        
        if not spec_file.exists():
            pytest.skip("alarmify.spec not found")
        
        content = spec_file.read_text(encoding='utf-8')
        
        # List of new dependencies to check
        new_dependencies = [
            'cloud_sync',
            'device_wake_manager',
            'logging_config',
        ]
        
        missing_deps = []
        for dep in new_dependencies:
            if dep not in content:
                missing_deps.append(dep)
        
        assert len(missing_deps) == 0, f"Missing dependencies in spec file: {missing_deps}"
    
    def test_gitignore_configured(self):
        """Test that .gitignore is properly configured for builds."""
        gitignore = PROJECT_ROOT / ".gitignore"
        
        if not gitignore.exists():
            pytest.skip(".gitignore not found")
        
        content = gitignore.read_text()
        
        required_entries = ['build/', 'dist/', 'Output/']
        
        for entry in required_entries:
            assert entry in content, f"'{entry}' not in .gitignore"


class TestInstallerCreation:
    """Test suite for installer creation and configuration."""
    
    def test_installer_script_exists(self):
        """Test that Inno Setup script exists."""
        iss_file = PROJECT_ROOT / "installer.iss"
        assert iss_file.exists(), "installer.iss not found"
    
    def test_installer_script_syntax(self):
        """Test that Inno Setup script has valid syntax."""
        iss_file = PROJECT_ROOT / "installer.iss"
        
        if not iss_file.exists():
            pytest.skip("installer.iss not found")
        
        content = iss_file.read_text(encoding='utf-8')
        
        # Check for required sections
        required_sections = ['[Setup]', '[Files]', '[Icons]']
        
        for section in required_sections:
            assert section in content, f"Required section '{section}' not found in installer.iss"
    
    def test_installer_created_successfully(self):
        """Test that installer was created successfully in Output directory."""
        if not OUTPUT_DIR.exists():
            pytest.skip("Output directory does not exist - installer not built")
        
        installer_files = list(OUTPUT_DIR.glob("AlarmifySetup*.exe"))
        
        assert len(installer_files) > 0, "No installer file found in Output directory"
        
        # Verify installer size is reasonable
        installer_path = installer_files[0]
        size_mb = installer_path.stat().st_size / (1024 * 1024)
        assert size_mb > 10, f"Installer too small: {size_mb:.2f} MB"
        assert size_mb < 600, f"Installer too large: {size_mb:.2f} MB"


class TestSmokeTests:
    """Test suite for basic smoke tests."""
    
    def test_executable_has_valid_pe_header(self, executable_path):
        """Test that executable has valid Windows PE header."""
        if not executable_path.exists():
            pytest.skip("Executable not built yet")
        
        with open(executable_path, 'rb') as f:
            # Verify MZ header
            dos_header = f.read(2)
            assert dos_header == b'MZ', "Missing MZ DOS header"
            
            # Verify PE signature
            f.seek(0x3C)
            pe_offset = struct.unpack('<I', f.read(4))[0]
            f.seek(pe_offset)
            pe_signature = f.read(4)
            assert pe_signature == b'PE\x00\x00', "Missing PE signature"
    
    def test_executable_is_not_corrupted(self, executable_path):
        """Test that executable file is readable and not corrupted."""
        if not executable_path.exists():
            pytest.skip("Executable not built yet")
        
        try:
            with open(executable_path, 'rb') as f:
                # Try to read the entire file
                data = f.read()
                assert len(data) > 0, "Executable file is empty"
        except Exception as e:
            pytest.fail(f"Failed to read executable: {e}")
    
    def test_basic_functionality_validation(self, executable_path):
        """Test that basic functionality is present in the executable."""
        if not executable_path.exists():
            pytest.skip("Executable not built yet")
        
        # Read executable and check for key strings
        with open(executable_path, 'rb') as f:
            content = f.read()
            
            # Check for presence of key components
            key_strings = [
                b'PyQt5',
                b'spotify',
                b'alarm',
            ]
            
            for key_str in key_strings:
                # Note: strings might be embedded in various ways
                # This is a basic check that should catch major issues
                assert key_str in content, f"Key component '{key_str.decode()}' not found in executable"


class TestCIConfiguration:
    """Test suite for CI/CD configuration."""
    
    def test_github_workflow_exists(self):
        """Test that GitHub Actions workflow exists."""
        workflow_file = PROJECT_ROOT / ".github" / "workflows" / "build.yml"
        assert workflow_file.exists(), "GitHub Actions workflow not found"
    
    def test_workflow_syntax(self):
        """Test that workflow YAML is valid."""
        workflow_file = PROJECT_ROOT / ".github" / "workflows" / "build.yml"
        
        if not workflow_file.exists():
            pytest.skip("Workflow file not found")
        
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not installed")
        
        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML in workflow file: {e}")


class TestDocumentation:
    """Test suite for build documentation."""
    
    def test_build_documentation_exists(self):
        """Test that BUILD.md exists."""
        build_doc = PROJECT_ROOT / "BUILD.md"
        assert build_doc.exists(), "BUILD.md not found"
    
    def test_agents_documentation_exists(self):
        """Test that AGENTS.md exists."""
        agents_doc = PROJECT_ROOT / "AGENTS.md"
        assert agents_doc.exists(), "AGENTS.md not found"


class TestVersionManager:
    """Test suite for version_manager.py utility."""
    
    def test_version_manager_exists(self):
        """Test that version_manager.py exists."""
        version_manager = PROJECT_ROOT / "version_manager.py"
        assert version_manager.exists(), "version_manager.py not found"
    
    def test_version_manager_syntax(self):
        """Test that version_manager.py has valid Python syntax."""
        version_manager = PROJECT_ROOT / "version_manager.py"
        
        if not version_manager.exists():
            pytest.skip("version_manager.py not found")
        
        try:
            with open(version_manager, 'r', encoding='utf-8') as f:
                compile(f.read(), str(version_manager), 'exec')
        except SyntaxError as e:
            pytest.fail(f"Syntax error in version_manager.py: {e}")
    
    def test_version_manager_can_import(self):
        """Test that version_manager.py can be imported."""
        try:
            sys.path.insert(0, str(PROJECT_ROOT))
            import version_manager
            assert hasattr(version_manager, 'VersionManager'), "VersionManager class not found"
        except Exception as e:
            pytest.fail(f"Failed to import version_manager: {e}")
        finally:
            if str(PROJECT_ROOT) in sys.path:
                sys.path.remove(str(PROJECT_ROOT))
    
    def test_version_manager_class_exists(self):
        """Test that VersionManager class exists and has required methods."""
        try:
            sys.path.insert(0, str(PROJECT_ROOT))
            from version_manager import VersionManager
            
            # Check that class exists
            assert VersionManager is not None
            
            # Check for required methods
            required_methods = [
                'get_version_from_iss',
                'set_version_in_iss',
                'parse_version',
                'format_version',
                'bump_version',
                'create_version_info_file',
            ]
            
            for method_name in required_methods:
                assert hasattr(VersionManager, method_name), f"Method '{method_name}' not found in VersionManager"
        except Exception as e:
            pytest.fail(f"Failed to verify VersionManager class: {e}")
        finally:
            if str(PROJECT_ROOT) in sys.path:
                sys.path.remove(str(PROJECT_ROOT))
    
    def test_version_manager_parse_version(self):
        """Test that VersionManager can parse version strings correctly."""
        try:
            sys.path.insert(0, str(PROJECT_ROOT))
            from version_manager import VersionManager
            
            vm = VersionManager(PROJECT_ROOT)
            
            # Test valid version strings
            assert vm.parse_version("1.0.0") == (1, 0, 0)
            assert vm.parse_version("2.5.13") == (2, 5, 13)
            assert vm.parse_version("0.1.0") == (0, 1, 0)
            
            # Test invalid version strings
            assert vm.parse_version("invalid") is None
            assert vm.parse_version("1.0") is None
            assert vm.parse_version("") is None
        except Exception as e:
            pytest.fail(f"Failed to test parse_version: {e}")
        finally:
            if str(PROJECT_ROOT) in sys.path:
                sys.path.remove(str(PROJECT_ROOT))
    
    def test_version_manager_format_version(self):
        """Test that VersionManager can format version components correctly."""
        try:
            sys.path.insert(0, str(PROJECT_ROOT))
            from version_manager import VersionManager
            
            vm = VersionManager(PROJECT_ROOT)
            
            # Test formatting
            assert vm.format_version(1, 0, 0) == "1.0.0"
            assert vm.format_version(2, 5, 13) == "2.5.13"
            assert vm.format_version(0, 1, 0) == "0.1.0"
        except Exception as e:
            pytest.fail(f"Failed to test format_version: {e}")
        finally:
            if str(PROJECT_ROOT) in sys.path:
                sys.path.remove(str(PROJECT_ROOT))
    
    def test_version_manager_get_version(self):
        """Test that VersionManager can retrieve current version."""
        try:
            sys.path.insert(0, str(PROJECT_ROOT))
            from version_manager import VersionManager
            
            vm = VersionManager(PROJECT_ROOT)
            version = vm.get_version_from_iss()
            
            if version:
                # If version exists, verify format
                assert re.match(r'^\d+\.\d+\.\d+', version), f"Invalid version format: {version}"
        except Exception as e:
            pytest.fail(f"Failed to test get_version_from_iss: {e}")
        finally:
            if str(PROJECT_ROOT) in sys.path:
                sys.path.remove(str(PROJECT_ROOT))


def test_build_scripts_executable():
    """Test that build scripts are executable."""
    scripts = [
        PROJECT_ROOT / "build_installer.py",
        PROJECT_ROOT / "version_manager.py",
    ]
    
    for script in scripts:
        assert script.exists(), f"Build script not found: {script}"
        
        # Test that script has valid Python syntax
        try:
            with open(script, 'r', encoding='utf-8') as f:
                compile(f.read(), str(script), 'exec')
        except SyntaxError as e:
            pytest.fail(f"Syntax error in {script.name}: {e}")


if __name__ == "__main__":
    # Allow running directly for quick tests
    pytest.main([__file__, '-v'])
