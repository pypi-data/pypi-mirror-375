"""
Flexible loader for condreg_cpp module that can handle different Python versions
"""
import os
import sys
import importlib.util
import glob
import platform

def import_condreg_cpp():
    """
    Import the condreg_cpp module, handling different Python versions and paths
    """
    # Get the directory of this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)  # This is the condreg-py-interface directory
    
    # Set environment variables for library paths
    condreg_cpp_build = os.path.abspath(os.path.join(parent_dir, '..', 'condreg-cpp', 'build'))
    if sys.platform == 'darwin':
        os.environ['DYLD_LIBRARY_PATH'] = condreg_cpp_build
    else:
        os.environ['LD_LIBRARY_PATH'] = condreg_cpp_build
    
    # Get platform-specific extension
    if sys.platform.startswith('win'):
        ext = '.pyd'
        platform_tag = 'win'
    elif sys.platform == 'darwin':
        ext = '.so'
        platform_tag = 'darwin'
    else:  # Linux and other Unix-like systems
        ext = '.so'
        platform_tag = 'linux'
    
    # Try to find a compatible .so/.pyd file
    py_version = f"{sys.version_info.major}{sys.version_info.minor}"
    
    # Places to look for the module
    search_dirs = [
        current_dir,  # First look in the current directory
        parent_dir,   # Then the parent directory
        os.path.join(current_dir, 'lib'),  # Then lib subdirectory
    ]
    
    # Look for version-specific files first, but only for the current platform
    version_patterns = [
        f"condreg_cpp.cpython-{py_version}-{platform_tag}{ext}",  # e.g., condreg_cpp.cpython-310-linux.so
        f"condreg_cpp.cpython-{py_version}*{ext}",  # e.g., condreg_cpp.cpython-310-x86_64-linux-gnu.so
        f"condreg_cpp{ext}"  # Generic pattern
    ]
    
    found_module = None
    
    # Loop through all directories and patterns
    for search_dir in search_dirs:
        for pattern in version_patterns:
            so_files = glob.glob(os.path.join(search_dir, pattern))
            if so_files:
                # Try each file until one works
                for so_path in so_files:
                    # Skip files that are clearly for a different platform
                    # Use more precise matching to avoid false positives (e.g., "darwin" contains "win")
                    filename = os.path.basename(so_path)
                    if platform_tag == 'linux' and ('-darwin' in filename or '-win' in filename or 'win32' in filename or 'win_amd64' in filename):
                        continue
                    elif platform_tag == 'darwin' and ('-linux' in filename or '-win' in filename or 'win32' in filename or 'win_amd64' in filename):
                        continue
                    elif platform_tag == 'win' and ('-linux' in filename or '-darwin' in filename):
                        continue
                    
                    try:
                        print(f"Trying to load module from: {so_path}")
                        spec = importlib.util.spec_from_file_location("condreg_cpp", so_path)
                        if spec is None:
                            continue
                        
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Test if module works by accessing a known function
                        if hasattr(module, 'kgrid'):
                            found_module = module
                            print(f"Successfully loaded module from {so_path}")
                            break
                    except Exception as e:
                        print(f"Error loading {so_path}: {e}")
                
                if found_module:
                    break
            
            if found_module:
                break
        
        if found_module:
            break
    
    # If we found a working module, return it
    if found_module:
        return found_module
    
    # If we get here, we couldn't find a working module, so we need to build one
    print("No compatible module found, attempting to build one")
    
    # Try to build the module - use the PARENT directory where setup.py is located
    import subprocess
    build_cmd = [sys.executable, "-m", "pip", "install", "-e", ".", "--verbose"]
    try:
        subprocess.check_call(build_cmd, cwd=parent_dir)  # Use parent_dir here, not current_dir
        
        # Try importing again after building
        for search_dir in search_dirs:
            for pattern in version_patterns:
                so_files = glob.glob(os.path.join(search_dir, pattern))
                if so_files:
                    for so_path in so_files:
                        # Skip files that are clearly for a different platform
                        filename = os.path.basename(so_path)
                        if platform_tag == 'linux' and ('-darwin' in filename or '-win' in filename or 'win32' in filename or 'win_amd64' in filename):
                            continue
                        elif platform_tag == 'darwin' and ('-linux' in filename or '-win' in filename or 'win32' in filename or 'win_amd64' in filename):
                            continue
                        elif platform_tag == 'win' and ('-linux' in filename or '-darwin' in filename):
                            continue
                        
                        try:
                            spec = importlib.util.spec_from_file_location("condreg_cpp", so_path)
                            if spec is None:
                                continue
                            
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            
                            # Test if module works
                            if hasattr(module, 'kgrid'):
                                return module
                        except Exception:
                            continue
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
    
    # If we get here, we couldn't load or build a compatible module
    py_version_str = ".".join(map(str, sys.version_info[:2]))
    raise ImportError(
        f"Could not load condreg_cpp module for Python {py_version_str} on {platform.system()}. "
        f"Please build the module manually with: cd {parent_dir} && pip install -e . --verbose"
    )
