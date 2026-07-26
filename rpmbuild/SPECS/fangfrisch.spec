%global debug_package %{nil}
# The PyInstaller bundle contains private copies of system libraries. Do not
# generate /usr/lib/.build-id links for those bundled ELF files, because their
# build IDs can collide with links owned by the host's libgcc and libstdc++ RPMs.
%global _build_id_links none

Name: fangfrisch
Version: 1.9.2
Release: 1%{?dist}
Summary: Update and verify unofficial ClamAV signatures
License: GPL-3.0-or-later
URL:     https://github.com/rseichter/fangfrisch

Source0: https://github.com/rseichter/fangfrisch/archive/refs/tags/%{version}.tar.gz
Source1: pyproject.toml
Source2: uv.lock
Source3: fangfrisch-entrypoint.py
Source4: fangfrisch-pyinstaller.spec
Source5: fangfrisch.service
Source6: fangfrisch.timer
Source7: fangfrisch.tmpfiles
Source8: fangfrisch.conf

BuildRequires:  systemd-rpm-macros

Requires: clamav
Requires: ca-certificates
Requires(post): clamav-filesystem
Requires(post): systemd
Requires(post): util-linux

%description
Fangfrisch (German for "freshly caught") is a sibling of the Clam Anti-Virus
freshclam utility. It allows downloading virus definition files that are not
official ClamAV canon, e.g. from Sanesecurity and URLhaus. Fangfrisch was
designed with security in mind, to be run by an unprivileged user only. 

%prep
%setup -q

# Add pinned RPM build dependencies and the PyInstaller input files to the
# upstream project.
install -m 0644 %{SOURCE1} pyproject.toml
install -m 0644 %{SOURCE2} uv.lock
install -m 0644 %{SOURCE3} fangfrisch-entrypoint.py
install -m 0644 %{SOURCE4} fangfrisch-pyinstaller.spec

%build
# Keep uv state separate for each target architecture when the build directory
# is shared between x86_64 and aarch64 builds.
export UV_CACHE_DIR="%{_builddir}/uv-cache.%{_arch}"
export UV_PYTHON_INSTALL_DIR="%{_builddir}/uv-python.%{_arch}"
export UV_PROJECT_ENVIRONMENT="%{_builddir}/uv-venv.%{_arch}"

# Use only the Python managed by uv; do not use the system Python at runtime.
# Match the Python version used by Fangfrisch's official CI workflow.
uv python install 3.14.6
uv sync --frozen --extra build --python 3.14.6
uv run --frozen --extra build pyinstaller \
    --clean \
    --noconfirm \
    fangfrisch-pyinstaller.spec

%install
install -d -m 0755 %{buildroot}%{_bindir}
install -d -m 0755 %{buildroot}%{_libexecdir}/fangfrisch
cp -a dist/fangfrisch/. %{buildroot}%{_libexecdir}/fangfrisch/

# Forward the user-facing command to the executable in the bundled runtime.
# Use a relative path from the installation target to avoid an RPM absolute
# symlink warning.
ln -s "$(realpath --relative-to="%{buildroot}%{_bindir}" \
    "%{buildroot}%{_libexecdir}/fangfrisch/fangfrisch")" \
    "%{buildroot}%{_bindir}/fangfrisch"

install -d -m 0750 %{buildroot}%{_sysconfdir}/fangfrisch
install -m 0640 %{SOURCE8} %{buildroot}%{_sysconfdir}/fangfrisch/fangfrisch.conf

install -D -m 0644 %{SOURCE5} %{buildroot}%{_unitdir}/fangfrisch.service
install -D -m 0644 %{SOURCE6} %{buildroot}%{_unitdir}/fangfrisch.timer
install -D -m 0644 %{SOURCE7} %{buildroot}%{_tmpfilesdir}/fangfrisch.conf

%post
%systemd_post fangfrisch.timer

# ClamAV owns this service account. Create it from ClamAV's sysusers
# definition when the dependency's transaction ordering has not done so yet.
if ! getent passwd clamupdate >/dev/null 2>&1 || \
   ! getent group clamupdate >/dev/null 2>&1; then
    systemd-sysusers /usr/lib/sysusers.d/clamav.conf
fi

# The service account must be able to read the configuration file.
chown root:clamupdate %{_sysconfdir}/fangfrisch
chmod 0750 %{_sysconfdir}/fangfrisch
chown root:clamupdate %{_sysconfdir}/fangfrisch/fangfrisch.conf
chmod 0640 %{_sysconfdir}/fangfrisch/fangfrisch.conf

# Create the directories after clamupdate exists so their ownership is correct.
systemd-tmpfiles --create %{_tmpfilesdir}/fangfrisch.conf

# Create the database schema using the dedicated user provided by ClamAV.
if [ ! -f %{_localstatedir}/lib/fangfrisch/db.sqlite ]; then
    runuser -u clamupdate -- /bin/sh -c \
        'umask 027; exec %{_bindir}/fangfrisch \
            --conf %{_sysconfdir}/fangfrisch/fangfrisch.conf initdb'
fi

# Keep the database readable only by clamupdate and its group.
if [ -f %{_localstatedir}/lib/fangfrisch/db.sqlite ]; then
    chmod 0640 %{_localstatedir}/lib/fangfrisch/db.sqlite
fi

%preun
%systemd_preun fangfrisch.timer

%postun
%systemd_postun fangfrisch.timer

%files
%license LICENSE
%doc README.rst
%{_bindir}/fangfrisch
%{_libexecdir}/fangfrisch/
%dir %attr(0750,root,root) %{_sysconfdir}/fangfrisch
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/fangfrisch/fangfrisch.conf
%{_unitdir}/fangfrisch.service
%{_unitdir}/fangfrisch.timer
%{_tmpfilesdir}/fangfrisch.conf

%changelog
* Sat Jul 25 2026 Jun Futagawa <jfut@integ.jp> - 1.9.2-1
- initial build
