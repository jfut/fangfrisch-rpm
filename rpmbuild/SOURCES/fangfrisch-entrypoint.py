"""Entry point for Fangfrisch launched by PyInstaller."""

from fangfrisch.__main__ import main


if __name__ == "__main__":
    # Launch Fangfrisch from the Python runtime bundled in the RPM.
    raise SystemExit(main())
