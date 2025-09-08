"""
CondrReg: A Python package for condition-number-regularized covariance estimation
Based on Won et al. (2013): Condition-number-regularized covariance estimation
"""
# Load the C++ module
from .condreg_loader import import_condreg_cpp
condreg_cpp = import_condreg_cpp()

# Import initialization modules
from .init_condreg import init_condreg
from .init_path import add_library_path as init_path

# Initialize paths if needed (not normally needed for installed packages)
init_path()

# Define what gets imported with "from condreg import *"
__all__ = ['init_condreg', 'kgrid', 'select_condreg', 'condreg', 'pfweights', 'transcost']

# For convenience, create an instance that users can import directly
model = init_condreg()

# Make key functions available at the package level
kgrid = model.kgrid
select_condreg = model.select_condreg
condreg = model.condreg
pfweights = model.pfweights
transcost = model.transcost
select_kmax = model.select_kmax

# Export relevant classes and functions, (Update this based on what should be exposed to users)
