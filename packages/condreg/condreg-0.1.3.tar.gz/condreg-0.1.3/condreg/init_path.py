import os
import sys

def add_library_path():
    # Get the directory of this file
    this_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Go up one level to the project root
    project_root = os.path.dirname(this_dir)
    
    # Path to the condreg-cpp build directory
    cpp_build_dir = os.path.abspath(os.path.join(project_root, '..', 'condreg-cpp', 'build'))
    
    # Add the build directory to LD_LIBRARY_PATH (Linux) or DYLD_LIBRARY_PATH (macOS)
    if sys.platform == 'darwin':
        # macOS
        if 'DYLD_LIBRARY_PATH' in os.environ:
            os.environ['DYLD_LIBRARY_PATH'] = cpp_build_dir + ':' + os.environ['DYLD_LIBRARY_PATH']
        else:
            os.environ['DYLD_LIBRARY_PATH'] = cpp_build_dir
    else:
        # Linux
        if 'LD_LIBRARY_PATH' in os.environ:
            os.environ['LD_LIBRARY_PATH'] = cpp_build_dir + ':' + os.environ['LD_LIBRARY_PATH']
        else:
            os.environ['LD_LIBRARY_PATH'] = cpp_build_dir
    
    # Add the directory to the Python path for direct imports
    sys.path.insert(0, project_root)

# Add the init_path function that's being imported in __init__.py
def init_path():
    """
    Initialize the library paths for CondrReg
    """
    # Call the add_library_path function
    add_library_path()
    
    # Return any values if needed, or just True to indicate success
    return True
