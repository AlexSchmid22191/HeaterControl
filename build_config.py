from __future__ import annotations

import base64
import re
import xml.etree.ElementTree as ElemT
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class OperatingSystemConfig:
    windows_xp: bool = False
    windows_server_2003: bool = False
    windows_vista: bool = False
    windows_server_2008: bool = False
    windows_7: bool = False
    windows_8: bool = False
    windows_10: bool = True
    windows_server_2016: bool = True
    windows_server_2019: bool = True
    windows_server_2022: bool = True
    windows_11: bool = True


@dataclass(frozen=True)
class ShortcutConfig:
    name: str
    target_file: str
    destination: str = "Desktop"


@dataclass(frozen=True)
class InstallerConfig:
    app_name: str
    company_name: str

    license_file: Path

    setup_icon: Path
    uninstaller_icon: Path

    languages: tuple[str, ...] = ("Deutsch", "English",)

    web_uri: str = "https://"

    default_installation_path: str = r"<ProgramFiles>\<Company>\<AppName>\\"

    default_shortcut_path: str = r"<Company>\<AppName>\\"

    operating_systems: OperatingSystemConfig = field(default_factory=OperatingSystemConfig)

    shortcut: ShortcutConfig | None = None

    compression_method: int = 0
    compression_level: int = 2


def _bool(value: bool) -> str:
    return "true" if value else "false"


def _format_size(size: int) -> str:
    """
    Produce approximately the same human-readable size format
    used by InstallForge.
    """
    units = ("B", "KB", "MB", "GB")

    value = float(size)

    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"

            rounded = round(value, 1)

            if rounded.is_integer():
                return f"{int(rounded)} {unit}"

            return f"{rounded} {unit}"

        value /= 1024

    raise RuntimeError("Unreachable")


def _installation_file_type(path: Path) -> str:
    if path.is_dir():
        return "[Folder]"

    suffix = path.suffix

    if suffix:
        return suffix[1:].lower()

    return "[File]"


def _add_text_element(parent: ElemT.Element, name: str, text: str,
                      attributes: dict[str, str] | None = None, ) -> ElemT.Element:
    element = ElemT.SubElement(parent, name, attributes or {}, )

    element.text = text
    return element


def _add_operating_systems(parent: ElemT.Element, config: OperatingSystemConfig, ) -> None:
    operating_system = ElemT.SubElement(parent, "OperatingSystem", {"check": "true"}, )

    values = {"WindowsXP":         config.windows_xp, "WindowsServer2003": config.windows_server_2003,
              "WindowsVista":      config.windows_vista, "WindowsServer2008": config.windows_server_2008,
              "Windows7":          config.windows_7, "Windows8": config.windows_8, "Windows10": config.windows_10,
              "WindowsServer2016": config.windows_server_2016, "WindowsServer2019": config.windows_server_2019,
              "WindowsServer2022": config.windows_server_2022, "Windows11": config.windows_11, }

    for name, enabled in values.items():
        _add_text_element(operating_system, name, _bool(enabled), )


def _add_installation_files(parent: ElemT.Element, dist_dir: Path, config: InstallerConfig, ) -> None:
    installation_files = ElemT.SubElement(parent, "InstallationFiles",
                                          {"defaultInstallationPath":            config.default_installation_path,
                                           "isDefaultInstallationPathAlterable": "true", }, )

    if not dist_dir.exists():
        raise FileNotFoundError(f"PyInstaller output does not exist: {dist_dir}")

    paths = sorted(dist_dir.iterdir(), key=lambda _path: (_path.is_file(), _path.name.casefold(),), )

    if not paths:
        raise RuntimeError(f"PyInstaller output directory is empty: {dist_dir}")

    for path in paths:
        if path.is_dir():
            size = "N/A"
        else:
            size = _format_size(path.stat().st_size)

        element = ElemT.SubElement(installation_files, "InstallationFile",
                                   {"size": size, "type": _installation_file_type(path), }, )

        element.text = str(path.resolve())


def _add_languages(parent: ElemT.Element, languages: tuple[str, ...], ) -> None:
    element = ElemT.SubElement(parent, "Languages", )

    for language in languages:
        _add_text_element(element, "Language", language, )


def _add_shortcuts(parent: ElemT.Element, config: InstallerConfig, ) -> None:
    shortcuts = ElemT.SubElement(parent, "Shortcuts",
                                 {"defaultPath":                           config.default_shortcut_path,
                                  "isDefaultPathAlterable":                "false",
                                  "isCreateStartmenuShortcutsForAllUsers": "true",
                                  "isCreateDesktopShortcutsForAllUsers":   "true", }, )

    if config.shortcut is None:
        return

    ElemT.SubElement(shortcuts, "Shortcut", {"destination":  config.shortcut.destination, "name": config.shortcut.name,
                                             "targetFile":   config.shortcut.target_file, "commandLineArguments": "",
                                             "iconFilePath": "", "iconIndex": "0", }, )


def generate_ifp(*, config: InstallerConfig, version: str, dist_dir: Path, installer_output: Path,
                 ifp_output: Path, ) -> None:
    """
    Generate a complete InstallForge project.
    """
    root = ElemT.Element("InstallForgeProject")

    # ---------------------------------------------------------
    # Metadata
    #
    # This is InstallForge's own project/product format version,
    # NOT the ElchiTools application version.
    # ---------------------------------------------------------

    ElemT.SubElement(root, "Metadata", {"productVersion": "1.5.0", "projectFileVersion": "2.0", }, )

    # ---------------------------------------------------------
    # Product information
    # ---------------------------------------------------------

    product_information = ElemT.SubElement(root, "ProductInformation", )

    _add_text_element(product_information, "Name", config.app_name, )

    _add_text_element(product_information, "Version", version, )

    _add_text_element(product_information, "CompanyName", config.company_name, )

    _add_text_element(product_information, "WebURI", config.web_uri, )

    # ---------------------------------------------------------
    # Installer configuration
    # ---------------------------------------------------------

    installer_configuration = ElemT.SubElement(root, "InstallerConfiguration", )

    # Prerequisites
    prerequisites = ElemT.SubElement(installer_configuration, "Prerequisites", )

    _add_operating_systems(prerequisites, config.operating_systems, )

    # User interface
    user_interface = ElemT.SubElement(installer_configuration, "UserInterface", )

    ElemT.SubElement(user_interface, "WizardImage", {"filePath": "<main>"}, )

    ElemT.SubElement(user_interface, "HeaderImage", {"filePath": "<main>"}, )

    ElemT.SubElement(user_interface, "Label", {"isEnabled": "true"}, )

    ElemT.SubElement(user_interface, "VisualStyle", {"isEnabled": "true"}, )

    # Installation files
    _add_installation_files(installer_configuration, dist_dir, config, )

    # Languages
    _add_languages(installer_configuration, config.languages, )

    # Currently unused sections
    ElemT.SubElement(installer_configuration, "Variables", )

    ElemT.SubElement(installer_configuration, "Commands", )

    ElemT.SubElement(installer_configuration, "Registry", )

    # Shortcuts
    _add_shortcuts(installer_configuration, config, )

    # Serials
    ElemT.SubElement(installer_configuration, "Serials",
                     {"isDialogEnabled": "false", "count": "1000", "mask": "#####-#####-#####-#####", }, )

    # Splash screen
    splash = ElemT.SubElement(installer_configuration, "SplashScreen",
                              {"isDialogEnabled": "false", "delayTime": "2", }, )

    ElemT.SubElement(splash, "Image", {"filePath": ""}, )

    ElemT.SubElement(splash, "Sound", {"isEnabled": "false", "filePath": "", }, )

    # License dialog.
    #
    # Your existing project has this disabled, so there's no
    # need to retain the large encoded RTF payload.
    license_element = ElemT.SubElement(installer_configuration, "License", {"isDialogEnabled": "true", })
    _add_text_element(license_element, "Data", _load_license_data(config.license_file), )

    ElemT.SubElement(license_element, "Data", )

    # Finish page
    finish = ElemT.SubElement(installer_configuration, "Finish", {"isRebootMachineEnabled": "false", }, )

    ElemT.SubElement(finish, "Program",
                     {"executableFilePath": r"<InstallPath>\\", "isLaunchEnabled": "false", "arguments": "", }, )

    # ---------------------------------------------------------
    # Uninstaller
    # ---------------------------------------------------------

    uninstaller = ElemT.SubElement(root, "UninstallerConfiguration", {"isPackaged": "true", }, )

    _add_text_element(uninstaller, "UninstallerExecutableFileName", "Uninstall", )

    _add_text_element(uninstaller, "OpenWebURIAfterUninstallation", "https://", {"isEnabled": "false", }, )

    ElemT.SubElement(uninstaller, "CustomDisplayIcon", {"isEnabled": "false", "iconFilePath": r"<InstallPath>\\", }, )

    # ---------------------------------------------------------
    # Visual Update
    # ---------------------------------------------------------

    visual_update = ElemT.SubElement(root, "VisualUpdateConfiguration", {"isPackaged": "false", }, )

    _add_text_element(visual_update, "ProductName", "<AppName>", )

    _add_text_element(visual_update, "ProductVersion", "<AppVersion>", )

    _add_text_element(visual_update, "Language", "0", )

    update_script_uris = ElemT.SubElement(visual_update, "UpdateScriptURIs", )

    _add_text_element(update_script_uris, "MainURI", "https://", )

    _add_text_element(update_script_uris, "FirstMirrorURI", "https://", )

    _add_text_element(update_script_uris, "SecondMirrorURI", "https://", )

    _add_text_element(visual_update, "updateExecutableFileName", "Update", )

    ElemT.SubElement(visual_update, "proEditionLicenseKey", )

    ElemT.SubElement(visual_update, "Program",
                     {"executableFilePath": "", "isLaunchEnabled": "false", "isTerminationEnabled": "false", }, )

    # ---------------------------------------------------------
    # Build configuration
    # ---------------------------------------------------------

    build_configuration = ElemT.SubElement(root, "BuildConfiguration", )

    _add_text_element(build_configuration, "SetupFilePath", str(installer_output.resolve()), )

    _add_text_element(build_configuration, "SetupIconPath", str(config.setup_icon.resolve()), )

    _add_text_element(build_configuration, "UninstallerIconPath", str(config.uninstaller_icon.resolve()), )

    ElemT.SubElement(build_configuration, "Compression",
                     {"method": str(config.compression_method), "level": str(config.compression_level), }, )

    ElemT.SubElement(build_configuration, "CodeSigning", {"isEnabled": "false", "signToolCommandLine": '/n "Subject" '
                                                                                                       '/tr '
                                                                                                       'http://timestamp.digicert.com '
                                                                                                       '/td sha256 '
                                                                                                       '/fd sha256 '
                                                                                                       '"<ExecutableFilePath>"', }, )

    # ---------------------------------------------------------
    # Write project
    # ---------------------------------------------------------

    ifp_output.parent.mkdir(parents=True, exist_ok=True, )

    tree = ElemT.ElementTree(root)

    ElemT.indent(tree, space="  ", )

    tree.write(ifp_output, encoding="UTF-8", xml_declaration=True, )


def _escape_rtf(text: str) -> str:
    """
    Escape arbitrary Unicode text for inclusion in an RTF document.
    """
    result: list[str] = []

    for char in text:
        code = ord(char)

        if char == "\\":
            result.append(r"\\")
        elif char == "{":
            result.append(r"\{")
        elif char == "}":
            result.append(r"\}")
        elif char == "\n":
            result.append(r"\line " if False else "\n")
        elif 32 <= code <= 126:
            result.append(char)
        else:
            # RTF uses signed 16-bit Unicode values.
            if code > 32767:
                code -= 65536

            result.append(fr"\u{code}?")

    return "".join(result)


def _markdown_to_rtf(markdown: str) -> str:
    """
    Convert the subset of Markdown typically used in a license file
    into a simple RTF document suitable for InstallForge.

    This intentionally keeps the conversion simple:
    headings become bold, bullets remain bullets, and paragraphs
    are preserved.
    """
    lines = markdown.splitlines()
    rtf_lines = [r"{\rtf1\ansi\deff0", r"{\fonttbl{\f0 Arial;}}", r"\fs20", ]

    for line in lines:
        stripped = line.strip()
        # Empty line -> paragraph break
        if not stripped:
            rtf_lines.append(r"\par")
            continue

        # Markdown headings
        heading = re.match(r"^(#{1,6})\s+(.*)$", stripped, )
        if heading:
            level = len(heading.group(1))
            text = _escape_rtf(heading.group(2))
            # Larger font for higher-level headings.
            size = {1: 32, 2: 28, 3: 24, }.get(level, 22)
            rtf_lines.append(fr"\b\fs{size} {text}\b0\fs20\par")
            continue

        # Markdown bullets
        bullet = re.match(r"^[-*+]\s+(.*)$", stripped, )
        if bullet:
            text = _escape_rtf(bullet.group(1))
            rtf_lines.append(fr"\bullet\tab {text}\par")
            continue

        # Basic numbered lists
        numbered = re.match(r"^\d+\.\s+(.*)$", stripped, )
        if numbered:
            text = _escape_rtf(stripped)
            rtf_lines.append(fr"{text}\par")
            continue

        # Normal paragraph
        text = _escape_rtf(stripped)
        rtf_lines.append(fr"{text}\par")

    rtf_lines.append("}")
    return "\n".join(rtf_lines)


def _load_license_data(license_file: Path, ) -> str:
    """
    Read Markdown license, convert it to RTF, and encode it in the
    format used by InstallForge's <License> <Data> element.
    """
    if not license_file.exists():
        raise FileNotFoundError(f"License file not found: {license_file}")

    markdown = license_file.read_text(encoding="utf-8")
    rtf = _markdown_to_rtf(markdown)

    return base64.b64encode(rtf.encode("utf-8")).decode("ascii")
