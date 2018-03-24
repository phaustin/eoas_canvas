import subprocess
from pathlib import Path
import site
import sys
import shutil
import os


if __name__ == "__main__":
    the_path=Path(sys.argv[0]).resolve()
    # ~/repos/eosc_canvas/tests/test_checkid.py
    the_path=the_path.parents[1]
    #~/repos/eosc_canvas
    sys.path.insert(0, str(the_path))
    site.removeduppaths()
    from e340py.check_ids import main
    args=None
    main(the_args=args)




      

