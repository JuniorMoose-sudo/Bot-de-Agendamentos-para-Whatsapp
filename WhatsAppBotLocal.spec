# -*- mode: python ; coding: utf-8 -*-

import sys
import os

# Caminho principal para evitar erros de import
base_path = os.path.abspath('.')

a = Analysis(
    ['app\\main.py'],
    pathex=[base_path],
    binaries=[],
    datas=[
        ('app', 'app'),
        ('data', 'data'),
    ],
    hiddenimports=[
        'selenium',
        'selenium.webdriver',
        'selenium.webdriver.common',
        'selenium.webdriver.support',
        'selenium.webdriver.chrome',
        'webdriver_manager',
        'webdriver_manager.chrome',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=1,  # Mais seguro que o 2
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='WhatsAppBotLocal',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Altere para True caso queira visualizar logs
)
