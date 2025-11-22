# -*- mode: python ; coding: utf-8 -*-

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
          name='ElchiTools',
          debug=False,
          bootloader_ignore_signals=False,
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
               name='ElchiTools')
