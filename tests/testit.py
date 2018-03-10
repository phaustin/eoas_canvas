import subprocess
from pathlib import Path
import site
import sys
import shutil
import os

def clean_build(tmpdir='.tmpdir',packagedir='.'):
    """
    do a clean build of the module in folder tmpdir

    Parameters
    ----------

    tmpdir: str
       name of directory for the install target
    
    Returns:
       None -- builds module as side effect
    """
    #
    #
    #
    tmpdir=str(Path(tmpdir).resolve())
    packagedir=str(Path(packagedir).resolve())
    try:
        shutil.rmtree(tmpdir)
    except FileNotFoundError:
         pass
    command=f"python -m pip -v install --target={tmpdir} --no-deps --ignore-installed {packagedir}"
    print(f'running: \n{command}')
    command = command.split()
    out=subprocess.check_output(command,stderr=subprocess.STDOUT,universal_newlines=True)
    sys.path.insert(0, tmpdir)
    site.removeduppaths()
    print(out)

if __name__ == "__main__":    
    clean_build()
    import e340py
    from e340py.dump_comments import main
    print(f'imported {e340py.__file__}')
    print(main(args='-h'))
    





      

