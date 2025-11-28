# -*- mode: python ; coding: utf-8 -*-

import sys, os
from PyInstaller.utils.win32.versioninfo import (
    VSVersionInfo,
    FixedFileInfo,
    StringFileInfo,
    StringTable,
    StringStruct,
    VarFileInfo,
    VarStruct,
)


project_root = os.path.abspath(os.getcwd())

sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

import src.appinfo

version_info = VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=src.appinfo.APP_VERSION_NUMERIC,
        prodvers=src.appinfo.APP_VERSION_NUMERIC,
        mask=0x3F,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        StringFileInfo([
            StringTable(
                '040904b0',
                [
                    StringStruct('CompanyName', src.appinfo.APP_COMPANY),
                    StringStruct('FileDescription', src.appinfo.APP_DESCRIPTION),
                    StringStruct('FileVersion', src.appinfo.APP_VERSION),
                    StringStruct('InternalName', src.appinfo.APP_NAME),
                    StringStruct('OriginalFilename', src.appinfo.APP_NAME),
                    StringStruct('ProductName', src.appinfo.APP_NAME),
                    StringStruct('ProductVersion', src.appinfo.APP_VERSION),
                ]
            )
        ]),
        VarFileInfo([
            VarStruct('Translation', [1033, 1200])
        ])
    ]
)

block_cipher = None


a = Analysis(['src/ElchiTools.py'],
             pathex=['.', 'src'],
             binaries=[],
             datas=[('src/Icons', 'Icons'), ('src/Fonts', 'Fonts'), ('License', 'License'), ('src/Styles', 'Styles')],
             hiddenimports=['pkg_resources.py2_warn'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name=src.appinfo.APP_NAME,
          debug=False,
          bootloader_ignore_signals=False,
          version=version_info,
          strip=False,
          upx=True,
          console=False,
          icon='src/Icons/Logo.ico',
          contents_directory='.')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name=src.appinfo.APP_NAME)
