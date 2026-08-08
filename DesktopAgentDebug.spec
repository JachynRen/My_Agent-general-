# -*- mode: python ; coding: utf-8 -*-
# Debug 版本打包配置：开启调试输出，输出到 dist-debug 目录，不覆盖 release 版本


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
    name='DesktopAgent',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # debug 版本保留控制台窗口查看日志
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
    name='DesktopAgent',
)
app = BUNDLE(
    coll,
    name='DesktopAgentDebug.app',
    icon=None,
    bundle_identifier=None,
)
