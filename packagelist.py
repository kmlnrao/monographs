import pkg_resources
import sys
import os

# Get standard library paths
stdlib_paths = [os.path.normcase(p) for p in sys.path if 'site-packages' not in p]

# Get installed packages
installed_packages = {dist.key for dist in pkg_resources.working_set}

# Filter out standard library modules
custom_packages = [pkg for pkg in installed_packages if pkg not in sys.builtin_module_names]
print("\n".join(sorted(custom_packages)))
