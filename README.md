# MacOS

For macOS versions **earlier than 11**, the system image needs to be created using:
[https://github.com/oneclickvirt/macos/blob/main/.github/workflows/build\_full\_iso.yml](https://github.com/oneclickvirt/macos/blob/main/.github/workflows/build_full_iso.yml)

For macOS versions **11 and later** (including Tahoe 26), the system image should be created using:
[https://github.com/oneclickvirt/macos/blob/main/appveyor.yml](https://github.com/oneclickvirt/macos/blob/main/appveyor.yml)

> **Note**: CircleCI support has been discontinued. AppVeyor is the only active CI for macOS 11+.

## Supported macOS Versions

| Version | Name | Build Code | Builder |
|---------|------|------------|---------|
| 10.13 | High Sierra | 17G66 | GitHub Actions |
| 10.14 | Mojave | 18F2059 | GitHub Actions |
| 10.15 | Catalina | 19D2064 | GitHub Actions |
| 11 | Big Sur | 20G1427 | AppVeyor |
| 12 | Monterey | 21H1123 | AppVeyor |
| 13 | Ventura | 22H313 | AppVeyor |
| 14 | Sonoma | 23H311 | AppVeyor |
| 15 | Sequoia | 24C101 | AppVeyor |
| 26 | **Tahoe** | 26A5247d *(beta placeholder)* | AppVeyor |

## Features

- **Image Size Optimization**:
  - `hdiutil compact` removes free space from the sparse image before conversion — typically saves several GB.
  - Safe metadata files (`.DS_Store`, `.Spotlight-V100`, `.fseventsd`, `.Trashes`) are cleaned up without affecting offline installation capability.
  - Final ISO is compressed with 7z LZMA2 (maximum compression).
- **Offline Installation**: The `--downloadassets` flag is preserved for macOS 11+, ensuring all required packages are bundled for completely offline installation.

## Setup

After forking this repository, set `IP` and `PASSWORD` in the AppVeyor project settings (for macOS 11+) or GitHub Actions secrets (for macOS ≤10.15), and the resulting image will be automatically uploaded to `/root/macos/` on your server after each build.

> **Note**: The server receiving the image needs at least **120 GB** of free disk space.

## Thanks to

* [https://github.com/corpnewt/gibMacOS](https://github.com/corpnewt/gibMacOS)
* [https://github.com/acidanthera/OpenCorePkg](https://github.com/acidanthera/OpenCorePkg)
