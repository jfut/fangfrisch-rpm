# Fangfrisch RPM Packaging

[![Tag](https://img.shields.io/github/tag/jfut/fangfrisch-rpm.svg)](https://github.com/jfut/fangfrisch-rpm/releases)
[![License](https://img.shields.io/badge/license-GPLv3-blue)](https://github.com/jfut/fangfrisch-rpm/blob/main/LICENSE)

[Fangfrisch](https://github.com/rseichter/fangfrisch) RPM Packaging for RHEL, AlmaLinux, Rocky Linux, and other compatible distributions.

The generated RPM bundles Fangfrisch, the Python runtime, and its Python dependencies under `/usr/libexec/fangfrisch`. Python, pip, venv, and uv are not required on the installation target.

## Installation

Fangfrisch depends on ClamAV. On RHEL-compatible distributions, enable the Extra Packages for Enterprise Linux (EPEL) repository first so that `dnf` can install this dependency:

```bash
dnf install epel-release
```

After enabling EPEL, download an RPM package from the [Releases](https://github.com/jfut/fangfrisch-rpm/releases) page, or configure the RPM repository below.

### Install with dnf-plugin-anyrepo

First, install [dnf-plugin-anyrepo](https://github.com/jfut/dnf-plugin-anyrepo) by following its installation instructions.

Next, import the RPM public signing key, add the repository, and install the package with `dnf`.

```bash
rpm --import https://raw.githubusercontent.com/jfut/fangfrisch-rpm/refs/heads/main/RPM-GPG-KEY-jfut-github
dnf-anyrepo add https://github.com/jfut/fangfrisch-rpm
dnf install fangfrisch
```

To upgrade the package, run:

```bash
dnf upgrade fangfrisch
```

### Configuration

For details, see [the official Fangfrisch documentation](https://rseichter.github.io/fangfrisch/).

The configuration file is located at `/etc/fangfrisch/fangfrisch.conf`.

To enable automatic updates of ClamAV definition files with Fangfrisch, enable the timer:

```bash
systemctl enable fangfrisch.timer
systemctl start fangfrisch.timer
```

By default, `fangfrisch.timer` runs once per hour, as configured in [`fangfrisch.timer`](rpmbuild/SOURCES/fangfrisch.timer). To change the execution interval, create a systemd override:

```bash
SYSTEMD_EDITOR=vi systemctl edit fangfrisch.timer
```

For example, to run Fangfrisch every 30 minutes, override the timer with the following settings:

```ini
[Timer]
OnCalendar=*:0/30
RandomizedDelaySec=29m
```

The Fangfrisch executable is installed at `/usr/bin/fangfrisch`, the database at `/var/lib/fangfrisch/db.sqlite`, and downloaded signatures at `/var/lib/clamav`.

## Build Usage

```bash
Usage:
    build [-d] [-s] [-h] [-p PLATFORM] BUILD_IMAGE_NAME

    Options:
        -d Debug mode.
        -s Sign RPMs after building.
        -p Docker platform, for example linux/arm64/v8.

    Signing environment variables:
        GPG_KEY_PATH Path to an ASCII-armored private key file.
        GPG_FINGERPRINT Optional GPG fingerprint or key ID used for rpmsign.
        GPG_PASSPHRASE Passphrase for the private key.

    Build for RHEL/AlmaLinux/Rocky Linux 10:
        build almalinux:10

    Build for RHEL/AlmaLinux/Rocky Linux 9:
        build almalinux:9

    Build for RHEL/AlmaLinux/Rocky Linux 8:
        build almalinux:8

    Build an aarch64 package:
        build -p linux/arm64/v8 almalinux:10
```

## Build RPM Packages with Docker

You can build RPM packages in Docker.

`build` starts an AlmaLinux container and runs `build-rpm` inside it.

`build-rpm` uses uv and PyInstaller during the SPEC `%build` phase to create a self-contained bundle and writes the results to `rpmbuild/RPMS` and `rpmbuild/SRPMS`.

```bash
BUILD_HOSTNAME=el10.example.org ./build almalinux:10
```

- Build and sign RPMs

```bash
export GPG_KEY_PATH=/path/to/rpm-signing-key.asc
read -r -s -p "GPG_PASSPHRASE: " GPG_PASSPHRASE; printf '\n'; export GPG_PASSPHRASE
BUILD_HOSTNAME=el10.example.org ./build -s almalinux:10
```

- Build an aarch64 package

```bash
BUILD_HOSTNAME=el10.example.org ./build -p linux/arm64/v8 almalinux:10
```

If the key file contains multiple secret keys, set `GPG_FINGERPRINT` explicitly.

- Debug shell

```bash
BUILD_HOSTNAME=el10.example.org ./build -d almalinux:10
/pkg/build-rpm /pkg/rpmbuild fangfrisch.spec
```

## Release

1. Run `git tag -s vX.Y.Z -m vX.Y.Z`.
2. Run `git push origin vX.Y.Z` and wait for the Release to be created.
3. Edit the created Release.
4. Press the `Generate release notes` button and edit the release notes.
5. Press the `Update release` button.

## License

GPLv3
