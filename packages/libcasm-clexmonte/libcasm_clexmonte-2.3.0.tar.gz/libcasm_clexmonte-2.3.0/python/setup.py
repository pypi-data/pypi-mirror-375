import os

__version__ = "2.3.0"

# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

# If on macosx, target 10.15 (ignored otherwise)
os.environ["MACOSX_DEPLOYMENT_TARGET"] = "10.15"

# extra_compile_args
extra_compile_args = [
    "-D_LIBCPP_DISABLE_AVAILABILITY",
    "--std=c++17",
]
if "CASM_EXTRA_COMPILE_ARGS" in os.environ:
    extra_compile_args += os.environ["CASM_EXTRA_COMPILE_ARGS"].split()

# extra_link_args

# Set absolute rpaths
# Expected installation layout example:
# C++ libraries:
# - <python package prefix>/libcasm/lib/libcasm_<name>.dylib
# - <python package prefix>/libcasm/lib64/libcasm_<name>.dylib
casm_prefix = os.getenv("CASM_PREFIX")
if casm_prefix is None:
    raise Exception("CASM_PREFIX not set")
rpath = os.path.join(casm_prefix, "lib")
rpath64 = os.path.join(casm_prefix, "lib64")
extra_link_args = [
    f"-Wl,-rpath,{rpath}",
    f"-Wl,-rpath,{rpath64}",
    "-lcasm_global",
    "-lcasm_crystallography",
    "-lcasm_composition",
    "-lcasm_clexulator",
    "-lcasm_configuration",
    "-lcasm_monte",
    "-lcasm_clexmonte",
]

# The main interface is through Pybind11Extension.
# * You can add cxx_std=11/14/17, and then build_ext can be removed.
# * You can set include_pybind11=false to add the include directory yourself,
#   say from a submodule.
#
# Note:
#   Sort input source files if you glob sources to ensure bit-for-bit
#   reproducible builds (https://github.com/pybind/python_example/pull/53)

ext_modules_params = {
    "define_macros": [
        ("VERSION_INFO", __version__),
    ],
    "cxx_std": 17,
    "library_dirs": [
        os.path.join(casm_prefix, "lib"),
        os.path.join(casm_prefix, "lib64"),
    ],
    "include_dirs": [
        os.path.join(casm_prefix, "include/casm/external"),
        os.path.join(casm_prefix, "include"),
    ],
    "extra_compile_args": extra_compile_args,
    "extra_link_args": extra_link_args,
}

ext_modules = [
    Pybind11Extension(
        "libcasm.clexmonte._clexmonte_system",
        ["src/clexmonte_system.cpp"],
        **ext_modules_params,
    ),
    Pybind11Extension(
        "libcasm.clexmonte._clexmonte_state",
        ["src/clexmonte_state.cpp"],
        **ext_modules_params,
    ),
    Pybind11Extension(
        "libcasm.clexmonte._clexmonte_functions",
        ["src/clexmonte_functions.cpp"],
        **ext_modules_params,
    ),
    Pybind11Extension(
        "libcasm.clexmonte._clexmonte_run_management",
        ["src/clexmonte_run_management.cpp"],
        **ext_modules_params,
    ),
    Pybind11Extension(
        "libcasm.clexmonte._clexmonte_monte_calculator",
        ["src/clexmonte_monte_calculator.cpp"],
        **ext_modules_params,
    ),
]
setup(
    name="libcasm-clexmonte",
    version=__version__,
    packages=[
        "libcasm",
        "libcasm.clexmonte",
        "libcasm.clexmonte.misc",
        "libcasm.clexmonte.site_iterators",
    ],
    install_requires=[
        "pybind11",
        "libcasm-global>=2.2.0",
        "libcasm-xtal>=2.2.0",
        "libcasm-composition>=2.2.0",
        "libcasm-clexulator>=2.2.0",
        "libcasm-configuration>=2.2.0",
        "libcasm-monte>=2.2.0",
    ],
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)
