# Code Signing Configuration

This document explains how to configure code signing for Alarmify releases.

## Why Code Signing?

Code signing provides:
- **Trust**: Users can verify the software comes from you
- **Security**: Prevents tampering and malware injection
- **Smart Screen**: Reduces Windows SmartScreen warnings
- **Professionalism**: Shows commitment to security

## Prerequisites

1. **Code Signing Certificate**
   - Purchase from a Certificate Authority (CA) like:
     - DigiCert
     - Sectigo (formerly Comodo)
     - GlobalSign
   - Cost: ~$100-500/year
   - Requires organization validation

2. **SignTool** (Windows SDK)
   - Usually installed with Visual Studio
   - Or download Windows SDK separately
   - Location: `C:\Program Files (x86)\Windows Kits\10\bin\<version>\x64\signtool.exe`

## Local Setup

### 1. Store Certificate Securely

```powershell
# Store certificate in Windows Certificate Store (recommended)
# Import via certmgr.msc or PowerShell:
Import-PfxCertificate -FilePath "path\to\cert.pfx" -CertStoreLocation Cert:\CurrentUser\My
```

### 2. Update build_installer.py

Uncomment the code signing sections and configure:

```python
def sign_file(file_path, cert_path=None, password=None):
    """Sign a file with a code signing certificate."""
    signtool = r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe"
    
    if cert_path:
        # Sign with PFX file
        cmd = [
            signtool, "sign",
            "/f", cert_path,
            "/p", password,
            "/tr", "http://timestamp.digicert.com",
            "/td", "sha256",
            "/fd", "sha256",
            str(file_path)
        ]
    else:
        # Sign with certificate from store
        cmd = [
            signtool, "sign",
            "/n", "Your Company Name",  # Certificate subject name
            "/tr", "http://timestamp.digicert.com",
            "/td", "sha256",
            "/fd", "sha256",
            str(file_path)
        ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0
```

### 3. Update installer.iss

Uncomment the SignTool configuration:

```ini
[Setup]
; Add this line to enable signing
SignTool=mysigntool

[Tools]
; Define the signing tool
SignTool=mysigntool /f "C:\path\to\cert.pfx" /p "password" /tr http://timestamp.digicert.com /td sha256 /fd sha256 $f
```

## GitHub Actions Setup

### 1. Store Certificate as Secret

1. Convert PFX to Base64:
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("cert.pfx")) | Out-File cert.txt
```

2. Add to GitHub Secrets:
   - Go to repository Settings → Secrets and variables → Actions
   - Add secret `CERT_BASE64` with the Base64 content
   - Add secret `CERT_PASSWORD` with certificate password

### 2. Update GitHub Actions Workflow

The workflow is already configured with placeholders. To enable:

1. Decode certificate in workflow:
```yaml
- name: Setup code signing
  run: |
    $certBytes = [Convert]::FromBase64String("${{ secrets.CERT_BASE64 }}")
    [IO.File]::WriteAllBytes("cert.pfx", $certBytes)
  shell: powershell
```

2. Enable signing steps by changing `if: false` to `if: true`

## Timestamp Servers

Always use timestamp servers to ensure signatures remain valid after certificate expires:

- **DigiCert**: http://timestamp.digicert.com
- **Sectigo**: http://timestamp.sectigo.com
- **GlobalSign**: http://timestamp.globalsign.com

## Verification

After signing, verify the signature:

```powershell
# Verify signature
signtool verify /pa /v "dist\Alarmify.exe"

# View certificate details
Get-AuthenticodeSignature "dist\Alarmify.exe" | Format-List *
```

## Self-Signed Certificates (Testing Only)

For testing only (not for distribution):

```powershell
# Create self-signed certificate
$cert = New-SelfSignedCertificate -Subject "CN=Test" -Type CodeSigning -CertStoreLocation Cert:\CurrentUser\My

# Export certificate
Export-PfxCertificate -Cert $cert -FilePath "test-cert.pfx" -Password (ConvertTo-SecureString -String "password" -Force -AsPlainText)
```

⚠️ **Warning**: Self-signed certificates will trigger SmartScreen warnings. Only use for testing.

## Troubleshooting

### "SignTool not found"
- Install Windows SDK
- Update path in scripts to match your installation

### "Invalid password"
- Verify certificate password
- Check if certificate requires hardware token

### "Timestamp server timeout"
- Try different timestamp server
- Check network connectivity
- Retry after a few minutes

### "Certificate not valid for code signing"
- Verify certificate has "Code Signing" purpose
- Check certificate hasn't expired

## Additional Resources

- [Microsoft: Sign your app package](https://docs.microsoft.com/en-us/windows/msix/package/sign-app-package-using-signtool)
- [DigiCert: Code Signing Best Practices](https://www.digicert.com/code-signing/best-practices)
- [Inno Setup: SignTool Documentation](https://jrsoftware.org/ishelp/index.php?topic=setup_signtool)
