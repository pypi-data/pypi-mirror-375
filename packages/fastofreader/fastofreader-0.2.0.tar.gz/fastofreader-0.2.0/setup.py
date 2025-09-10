from setuptools import setup, Extension
from Cython.Build import cythonize
import os

CFLAGS  = os.environ.get("FASTOPS_CFLAGS", "").split()
LDFLAGS = os.environ.get("FASTOPS_LDFLAGS", "").split()

extensions = [
    Extension(
        name="fastofreader.core",
        sources=["src/fastofreader/core.pyx"],
        extra_compile_args=CFLAGS,
        extra_link_args=LDFLAGS,
    )
]

setup(
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            "language_level": "3",
            "boundscheck": False,
            "wraparound": False,
            "initializedcheck": False,
            "nonecheck": False,
            "cdivision": True,
            "embedsignature": True,
            "infer_types": True,
        },
    ),
)
