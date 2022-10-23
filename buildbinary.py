import PyInstaller.__main__

PyInstaller.__main__.run([
    'policies.py',
    '--windowed',
    '--noconfirm',
    # '--onedir',
    '--onefile'
])