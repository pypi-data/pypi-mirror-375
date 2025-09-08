#!/usr/bin/env python3
"""
Cross-platform build script for condreg-cpp library.
This script builds the C++ library required by the Python bindings.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    """Run a command and handle errors"""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, cwd=cwd, check=check, 
                              capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        raise

def find_cmake():
    """Find cmake executable"""
    cmake_names = ['cmake', 'cmake3']
    for name in cmake_names:
        if shutil.which(name):
            return name
    raise RuntimeError("CMake not found. Please install CMake.")

def detect_visual_studio_generator():
    """Detect available Visual Studio generator for CMake"""
    # Try to detect Visual Studio installations
    vs_versions = [
        ("Visual Studio 17 2022", [
            "C:/Program Files/Microsoft Visual Studio/2022/Enterprise",
            "C:/Program Files/Microsoft Visual Studio/2022/Professional", 
            "C:/Program Files/Microsoft Visual Studio/2022/Community",
            "C:/Program Files/Microsoft Visual Studio/2022/BuildTools"
        ]),
        ("Visual Studio 16 2019", [
            "C:/Program Files (x86)/Microsoft Visual Studio/2019/Enterprise",
            "C:/Program Files (x86)/Microsoft Visual Studio/2019/Professional",
            "C:/Program Files (x86)/Microsoft Visual Studio/2019/Community",
            "C:/Program Files (x86)/Microsoft Visual Studio/2019/BuildTools"
        ]),
        ("Visual Studio 15 2017", [
            "C:/Program Files (x86)/Microsoft Visual Studio/2017/Enterprise",
            "C:/Program Files (x86)/Microsoft Visual Studio/2017/Professional",
            "C:/Program Files (x86)/Microsoft Visual Studio/2017/Community",
            "C:/Program Files (x86)/Microsoft Visual Studio/2017/BuildTools"
        ])
    ]
    
    for generator, paths in vs_versions:
        for path in paths:
            if os.path.exists(path):
                print(f"Found Visual Studio installation: {path}")
                return generator
    
    # Fallback: try to use cmake to detect generators
    try:
        cmake = find_cmake()
        result = subprocess.run([cmake, "--help"], capture_output=True, text=True)
        if result.returncode == 0:
            output = result.stdout
            if "Visual Studio 17 2022" in output:
                return "Visual Studio 17 2022"
            elif "Visual Studio 16 2019" in output:
                return "Visual Studio 16 2019"
            elif "Visual Studio 15 2017" in output:
                return "Visual Studio 15 2017"
    except Exception as e:
        print(f"Warning: Could not detect Visual Studio version via cmake: {e}")
    
    # Final fallback
    print("Warning: Could not detect Visual Studio version, using default")
    return "Visual Studio 17 2022"

def build_cpp_library():
    """Build the C++ library"""
    # Get paths - handle both cases: running from condreg-py-interface or from repo root
    script_dir = Path(__file__).parent
    
    # Try different possible locations for condreg-cpp
    possible_cpp_dirs = [
        script_dir.parent / "condreg-cpp",  # When run from condreg-py-interface
        script_dir / "condreg-cpp",         # When run from repo root (cibuildwheel)
        Path.cwd() / "condreg-cpp"          # Fallback to current working directory
    ]
    
    cpp_dir = None
    for candidate in possible_cpp_dirs:
        if candidate.exists() and (candidate / "CMakeLists.txt").exists():
            cpp_dir = candidate
            break
    
    if cpp_dir is None:
        print("Searched for condreg-cpp in:")
        for candidate in possible_cpp_dirs:
            print(f"  {candidate} - {'exists' if candidate.exists() else 'not found'}")
        raise RuntimeError("C++ source directory not found")
    
    build_dir = cpp_dir / "build"
    
    print(f"Building C++ library in: {cpp_dir}")
    print(f"Platform: {platform.system()} {platform.machine()}")
    
    # Clean build directory if CMakeCache.txt exists and has wrong paths
    cmake_cache = build_dir / "CMakeCache.txt"
    if cmake_cache.exists():
        try:
            with open(cmake_cache, 'r') as f:
                cache_content = f.read()
                # Check if cache contains different source directory
                if str(cpp_dir) not in cache_content:
                    print("Cleaning stale CMake cache...")
                    shutil.rmtree(build_dir)
        except Exception as e:
            print(f"Warning: Could not check CMake cache: {e}")
            print("Cleaning build directory to be safe...")
            shutil.rmtree(build_dir, ignore_errors=True)
    
    # Create build directory
    build_dir.mkdir(exist_ok=True)
    
    # Find cmake
    cmake = find_cmake()
    
    # Configure build
    cmake_args = [cmake, ".."]
    
    # Platform-specific configuration
    if platform.system() == "Windows":
        # Use Visual Studio generator on Windows - detect available version
        vs_generator = detect_visual_studio_generator()
        cmake_args.extend([
            "-G", vs_generator,
            "-A", "x64",
            "-DCMAKE_BUILD_TYPE=Release"
        ])
    else:
        # Use Unix Makefiles or Ninja on Unix-like systems
        if shutil.which("ninja"):
            cmake_args.extend(["-G", "Ninja"])
        cmake_args.extend([
            "-DCMAKE_BUILD_TYPE=Release",
            "-DCMAKE_POSITION_INDEPENDENT_CODE=ON"
        ])
    
    # Add Eigen path if specified
    if "EIGEN_INCLUDE_DIR" in os.environ:
        eigen_path = os.environ["EIGEN_INCLUDE_DIR"]
        cmake_args.append(f"-DEIGEN3_INCLUDE_DIR={eigen_path}")
    
    print("Configuring with CMake...")
    run_command(cmake_args, cwd=build_dir)
    
    # Build
    build_args = [cmake, "--build", ".", "--config", "Release"]
    
    # Add parallel build on Unix
    if platform.system() != "Windows":
        import multiprocessing
        build_args.extend(["--", f"-j{multiprocessing.cpu_count()}"])
    
    print("Building...")
    run_command(build_args, cwd=build_dir)
    
    # Verify library was built
    if platform.system() == "Windows":
        lib_patterns = ["Release/condreg.lib", "Debug/condreg.lib", "condreg.lib"]
    else:
        lib_patterns = ["libcondreg.a", "libcondreg.so"]
    
    lib_found = False
    for pattern in lib_patterns:
        lib_path = build_dir / pattern
        if lib_path.exists():
            print(f"Library built successfully: {lib_path}")
            lib_found = True
            break
    
    if not lib_found:
        print("Warning: Could not find built library file")
        print("Contents of build directory:")
        for item in build_dir.rglob("*"):
            if item.is_file():
                print(f"  {item.relative_to(build_dir)}")
    
    return True

def install_dependencies():
    """Install build dependencies"""
    print("Installing build dependencies...")
    
    # Check for required tools
    required_tools = []
    
    if not shutil.which("cmake"):
        required_tools.append("cmake")
    
    if platform.system() == "Windows":
        # Check for Visual Studio or Build Tools
        vs_paths = [
            "C:/Program Files (x86)/Microsoft Visual Studio/2019",
            "C:/Program Files/Microsoft Visual Studio/2022",
            "C:/BuildTools"
        ]
        vs_found = any(os.path.exists(path) for path in vs_paths)
        if not vs_found:
            print("Warning: Visual Studio or Build Tools for Visual Studio not found")
            print("Please install Visual Studio 2019 or later, or Build Tools for Visual Studio")
    
    if required_tools:
        print(f"Missing required tools: {', '.join(required_tools)}")
        print("Please install them using your system package manager:")
        
        if platform.system() == "Darwin":  # macOS
            print("  brew install cmake")
        elif platform.system() == "Linux":
            print("  sudo apt-get install cmake build-essential  # Ubuntu/Debian")
            print("  sudo yum install cmake gcc-c++             # CentOS/RHEL")
        elif platform.system() == "Windows":
            print("  Install CMake from https://cmake.org/download/")
            print("  Install Visual Studio Build Tools")
        
        return False
    
    return True

def main():
    """Main function"""
    print("=== Cross-platform C++ Library Builder ===")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--check-deps":
        success = install_dependencies()
        sys.exit(0 if success else 1)
    
    try:
        if not install_dependencies():
            print("Please install missing dependencies and try again.")
            sys.exit(1)
        
        build_cpp_library()
        print("Build completed successfully!")
        
    except Exception as e:
        print(f"Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 