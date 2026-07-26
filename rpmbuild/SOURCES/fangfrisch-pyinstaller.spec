from PyInstaller.utils.hooks import collect_all


# Collect data files and hidden imports for Fangfrisch and its dependencies.
fangfrisch_datas, fangfrisch_binaries, fangfrisch_hiddenimports = collect_all("fangfrisch")
sqlalchemy_datas, sqlalchemy_binaries, sqlalchemy_hiddenimports = collect_all("sqlalchemy")
requests_datas, requests_binaries, requests_hiddenimports = collect_all("requests")
certifi_datas, certifi_binaries, certifi_hiddenimports = collect_all("certifi")

analysis = Analysis(
    ["fangfrisch-entrypoint.py"],
    pathex=["src"],
    binaries=(
        fangfrisch_binaries
        + sqlalchemy_binaries
        + requests_binaries
        + certifi_binaries
    ),
    datas=(fangfrisch_datas + sqlalchemy_datas + requests_datas + certifi_datas),
    hiddenimports=(
        fangfrisch_hiddenimports
        + sqlalchemy_hiddenimports
        + requests_hiddenimports
        + certifi_hiddenimports
    ),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(analysis.pure)

executable = EXE(
    pyz,
    analysis.scripts,
    [],
    name="fangfrisch",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    exclude_binaries=True,
)

# Place the executable and runtime in the same directory for an onedir build.
COLLECT(
    executable,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    name="fangfrisch",
)
