# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),  # configディレクトリ全体をコピー
        ('src/modules', 'src/modules'),  # modulesディレクトリをコピー
        ('src/utils', 'src/utils'),  # utilsディレクトリをコピー
    ],
    hiddenimports=[
        'selenium',
        'pandas',
        'google.oauth2.credentials',
        'google.oauth2.service_account',
        'googleapiclient.discovery',
        'chromedriver_binary',
        'dotenv',
        'httpx',
        'openai',
        'tqdm',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='lstep_dl',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)