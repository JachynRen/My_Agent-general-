# -*- mode: python ; coding: utf-8 -*-
# Windows Debug 版：文件夹模式（onedir），保留控制台查看日志
# 输出到 dist-debug/DesktopAgentDebug/

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DesktopAgentDebug',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,           # Debug 版保留控制台查看日志
    disable_windowed_traceback=True,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DesktopAgentDebug',
)
