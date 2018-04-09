from pathlib import Path
#
# open the VERSION file and read it into e340py.__version__
#
version_file=Path(__file__).parent / Path('VERSION')

if not version_file.is_file():
    with open(version_file,'w') as f:
        __version__ = 'no_version'
        f.write(__version__)
else:
    with open(version_file) as f:
        __version__=f.read().strip()

