from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
import sys
import os
import platform
import pybind11

__version__ = '0.1.3'

# Locate condreg-cpp
root_dir = os.path.dirname(os.path.abspath(__file__))
condreg_cpp_dir = os.path.abspath(os.path.join(root_dir, '..', 'condreg-cpp'))
condreg_cpp_include = os.path.join(condreg_cpp_dir, 'include')

# Cross-platform Eigen detection
def find_eigen_include():
    """Find Eigen include directory across different platforms"""
    possible_paths = []
    
    if platform.system() == "Darwin":  # macOS
        possible_paths.extend([
            '/opt/homebrew/include/eigen3',  # Homebrew ARM64
            '/usr/local/include/eigen3',     # Homebrew Intel
            '/opt/local/include/eigen3',     # MacPorts
        ])
    elif platform.system() == "Linux":
        possible_paths.extend([
            '/usr/include/eigen3',           # Ubuntu/Debian
            '/usr/local/include/eigen3',     # Manual install
            '/opt/eigen3/include',           # Custom install
        ])
    elif platform.system() == "Windows":
        possible_paths.extend([
            'C:/vcpkg/installed/x64-windows/include/eigen3',  # vcpkg
            'C:/eigen3/include',             # Manual install
            'C:/Program Files/Eigen3/include/eigen3',
        ])
    
    # Check environment variable first
    if 'EIGEN_INCLUDE_DIR' in os.environ:
        eigen_path = os.environ['EIGEN_INCLUDE_DIR']
        if os.path.exists(eigen_path):
            return eigen_path
    
    # Try to find Eigen in possible paths
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Try to use conda/pip installed eigen if available
    try:
        import numpy
        numpy_include = numpy.get_include()
        conda_eigen = os.path.join(os.path.dirname(numpy_include), 'eigen3')
        if os.path.exists(conda_eigen):
            return conda_eigen
    except ImportError:
        pass
    
    # Fallback: assume system has eigen in standard location
    print("Warning: Could not find Eigen3. Assuming it's in system include path.")
    return None

EIGEN_INCLUDE_DIR = find_eigen_include()

# Detect Python version
python_version = ".".join(map(str, sys.version_info[:2]))
print(f"Building for Python {python_version}")
print(f"Platform: {platform.system()} {platform.machine()}")
if EIGEN_INCLUDE_DIR:
    print(f"Using Eigen headers from: {EIGEN_INCLUDE_DIR}")
else:
    print("Using system Eigen headers")
print(f"Using condreg-cpp from: {condreg_cpp_dir}")

class get_pybind_include:
    """Helper class to determine the pybind11 include path"""
    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        return pybind11.get_include(self.user)

def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler."""
    import tempfile
    import subprocess
    with tempfile.NamedTemporaryFile('w', suffix='.cpp', delete=False) as f:
        f.write('int main (int argc, char **argv) { return 0; }')
        fname = f.name
    try:
        compiler.compile([fname], extra_postargs=[flagname])
        return True
    except Exception:
        return False
    finally:
        try:
            os.unlink(fname)
            os.unlink(fname + '.o')  # Unix
        except:
            try:
                os.unlink(fname.replace('.cpp', '.obj'))  # Windows
            except:
                pass

def cpp_flag(compiler):
    """Return the -std=c++[11/14/17] compiler flag."""
    if platform.system() == "Windows":
        return '/std:c++14'  # MSVC syntax
    
    flags = ['-std=c++14', '-std=c++11']
    for flag in flags:
        if has_flag(compiler, flag): 
            return flag
    raise RuntimeError('Unsupported compiler -- at least C++11 support is needed!')

class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""
    c_opts = {
        'msvc': ['/EHsc', '/bigobj'],
        'unix': [],
    }
    l_opts = {
        'msvc': [],
        'unix': [],
    }

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        link_opts = self.l_opts.get(ct, [])
        
        if ct == 'unix':
            opts.append('-DVERSION_INFO="%s"' % self.distribution.get_version())
            opts.append(cpp_flag(self.compiler))
            if has_flag(self.compiler, '-fvisibility=hidden'):
                opts.append('-fvisibility=hidden')
            
            # Platform-specific optimizations
            if platform.system() == "Darwin":  # macOS
                opts.extend(['-stdlib=libc++', '-mmacosx-version-min=10.9'])
                link_opts.extend(['-stdlib=libc++', '-mmacosx-version-min=10.9'])
            elif platform.system() == "Linux":
                opts.extend(['-fPIC'])
                
        elif ct == 'msvc':
            opts.append('/DVERSION_INFO=\\"%s\\"' % self.distribution.get_version())
            opts.append(cpp_flag(self.compiler))
        
        for ext in self.extensions:
            ext.extra_compile_args = opts
            ext.extra_link_args = link_opts
            
            # Add platform-specific runtime library paths
            if ct == 'unix' and platform.system() != "Windows":
                if platform.system() == "Darwin":
                    ext.extra_link_args.append('-Wl,-rpath,@loader_path')
                elif platform.system() == "Linux":
                    ext.extra_link_args.append('-Wl,-rpath,$ORIGIN')
                    
        build_ext.build_extensions(self)

def get_library_info():
    """Get platform-specific library information"""
    system = platform.system()
    
    if system == "Windows":
        lib_name = 'condreg'
        lib_dirs = [os.path.join(condreg_cpp_dir, 'build', 'Release'),
                   os.path.join(condreg_cpp_dir, 'build', 'Debug'),
                   os.path.join(condreg_cpp_dir, 'build')]
        runtime_dirs = []
    else:  # Unix-like (Linux, macOS)
        lib_name = 'condreg'
        lib_dirs = [os.path.join(condreg_cpp_dir, 'build')]
        runtime_dirs = [os.path.join(condreg_cpp_dir, 'build')]
    
    return lib_name, lib_dirs, runtime_dirs

# Build extensions by default (not just when build_ext is explicitly requested)
lib_name, lib_dirs, runtime_dirs = get_library_info()

include_dirs = [
    condreg_cpp_include,
    get_pybind_include(),
    get_pybind_include(user=True),
]

# Add Eigen include directory if found
if EIGEN_INCLUDE_DIR:
    include_dirs.append(EIGEN_INCLUDE_DIR)

ext_modules = [
    Extension(
        'condreg_cpp',
        ['src/bindings.cpp'],
        include_dirs=include_dirs,
        libraries=[lib_name],
        library_dirs=lib_dirs,
        runtime_library_dirs=runtime_dirs,
        language='c++',
    ),
]

setup(
    name='condreg',
    version=__version__,
    description='Python bindings for condreg-cpp: Condition Number Regularized Covariance Estimation',
    long_description=open('README.md').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    author='Sang Yun Oh, Lixing Guo',
    author_email='syoh@ucsb.edu',
    url='https://github.com/dddlab/CondReg',
    packages=find_packages(),
    ext_modules=ext_modules,
    install_requires=['pybind11>=2.4', 'numpy>=1.18.0'],
    cmdclass={'build_ext': BuildExt},
    zip_safe=False,
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: C++',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
)
