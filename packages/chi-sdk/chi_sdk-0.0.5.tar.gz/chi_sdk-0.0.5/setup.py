from setuptools import setup
from setuptools.dist import Distribution


class BinaryDistribution(Distribution):
    def has_ext_modules(self):
        # Mark wheel as platform-specific when binary is included
        import os

        binary_exists = os.path.exists("src/chi_sdk/bin/chi-tui") or os.path.exists(
            "src/chi_sdk/bin/chi-tui.exe"
        )
        return binary_exists


setup(distclass=BinaryDistribution)
