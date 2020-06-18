# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['HeaterControl.py'],
             pathex=['C:\\Users\\Alex\\PycharmProjects\\HeaterControl'],
             binaries=[],
             datas=[('App.mplstyle', '.'), ('Icons', 'Icons')],
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
          name='HeaterControl',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
<<<<<<< HEAD
          console=False )
=======
          console=False,
          icon='Icons/Logo.ico')
>>>>>>> 3812a9c65e8725e80c54d06e166a5da134d0988b
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='HeaterControl')
