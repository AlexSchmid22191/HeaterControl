from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from appinfo import APP_BUILD_NAME, APP_COMPANY, APP_NAME, APP_VERSION
from build_config import generate_ifp, InstallerConfig, ShortcutConfig

ROOT = Path(__file__).resolve().parent

SPEC_FILE = ROOT / "ElchiTools.spec"

DIST_DIR = ROOT / "dist" / f'{APP_BUILD_NAME}'
BUILD_DIR = ROOT / "build"
RELEASE_DIR = ROOT / "release"

GENERATED_IFP = BUILD_DIR / "ElchiTools.ifp"
APP_EXE = DIST_DIR / "ElchiTools.exe"

INSTALLFORGE = Path(r"C:\Program Files (x86)\solicus\InstallForge\bin\ifbuildx86.exe")

INSTALLER_CONFIG = InstallerConfig(app_name=APP_NAME, company_name=APP_COMPANY,
                                   setup_icon=ROOT / "src" / "Icons" / "Logo.ico",
                                   uninstaller_icon=ROOT / "src" / "Icons" / "Logo.ico",
                                   languages=("Deutsch", "English",),
                                   shortcut=ShortcutConfig(name="ElchiTools", destination="Desktop",
                                                           target_file=r"<InstallPath>\ElchiTools.exe"),
                                   license_file=ROOT / "License" / "License.md")


def clean_build_output() -> None:
    """
    Remove stale PyInstaller and generated installer data.
    """
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    if GENERATED_IFP.exists():
        GENERATED_IFP.unlink()


def build_pyinstaller() -> None:
    print("Building application with PyInstaller...")

    subprocess.run([sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", str(SPEC_FILE)],
                   cwd=ROOT, check=True)

    if not APP_EXE.exists():
        raise RuntimeError("PyInstaller completed successfully but "
                           f"{APP_EXE} does not exist.")


def generate_installforge_project(version: str, ) -> Path:
    print("Generating InstallForge project...")

    RELEASE_DIR.mkdir(parents=True, exist_ok=True, )
    installer_output = (RELEASE_DIR / f'{APP_BUILD_NAME}_Installer.exe')
    generate_ifp(config=INSTALLER_CONFIG, version=version, dist_dir=DIST_DIR, installer_output=installer_output,
                 ifp_output=GENERATED_IFP, )

    print(f"Generated: {GENERATED_IFP}")

    return installer_output


def build_installer() -> None:
    if not INSTALLFORGE.exists():
        raise FileNotFoundError("InstallForge CLI builder not found:\n"
                                f"{INSTALLFORGE}")

    print("Building installer with InstallForge...")

    subprocess.run([str(INSTALLFORGE), "-i", str(GENERATED_IFP), ], cwd=ROOT, check=True, )


def verify_installer(installer: Path, ) -> None:
    if not installer.exists():
        raise RuntimeError("InstallForge completed, but the expected "
                           f"installer does not exist:\n{installer}")

    size_mb = (installer.stat().st_size / 1024 / 1024)

    print()
    print("Build successful")
    print(f"Installer: {installer}")
    print(f"Size:      {size_mb:.1f} MB")


def build_release(version: str, ) -> None:
    print()
    print(f"Building ElchiTools {version}")
    print("=" * 50)

    clean_build_output()
    build_pyinstaller()
    installer = (generate_installforge_project(version))
    build_installer()
    verify_installer(installer)


def main() -> None:
    build_release(APP_VERSION)


if __name__ == "__main__":
    main()
