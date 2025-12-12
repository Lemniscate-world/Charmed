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


# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
EXE_PATH = DIST_DIR / "Alarmify.exe"


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
        import re
        match = re.search(r'#define MyAppVersion "([^"]+)"', content)
        
        assert match, "Version not found in installer.iss"
        version = match.group(1)
        
        # Validate version format (semantic versioning)
        version_pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$'
        assert re.match(version_pattern, version), f"Invalid version format: {version}"


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
    
    def test_gitignore_configured(self):
        """Test that .gitignore is properly configured for builds."""
        gitignore = PROJECT_ROOT / ".gitignore"
        
        if not gitignore.exists():
            pytest.skip(".gitignore not found")
        
        content = gitignore.read_text()
        
        required_entries = ['build/', 'dist/', 'Output/']
        
        for entry in required_entries:
            assert entry in content, f"'{entry}' not in .gitignore"


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
    
    def test_release_documentation_exists(self):
        """Test that RELEASE.md exists."""
        release_doc = PROJECT_ROOT / "RELEASE.md"
        assert release_doc.exists(), "RELEASE.md not found"
    
    def test_code_signing_documentation_exists(self):
        """Test that code signing documentation exists."""
        signing_doc = PROJECT_ROOT / "code_signing_config.md"
        assert signing_doc.exists(), "code_signing_config.md not found"


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
