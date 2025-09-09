import os
import shutil

def custom_init():
    """
    setup utility for CPSC 103 to be run at the start of the course via
    our setup.ipynb file.
    
    (Warning: If you have your own Jupyter customizations, this may unrecoverably
    override them.)
    """
    
    srcdir = os.path.dirname(__file__)

    src = os.path.join(srcdir, 'custom.js')
    dstdir = os.path.expanduser("~/.jupyter/custom/")
    try:
        os.makedirs(dstdir)
    except:
        pass
    shutil.copy(src, dstdir)

    src = os.path.join(srcdir, 'ipython_config.py')
    dstdir = os.path.expanduser("~/.ipython/profile_default/")
    shutil.copy(src, dstdir)

# be aware that the overall cs103 library has its own __all__
__all__ = ['custom_init'] 