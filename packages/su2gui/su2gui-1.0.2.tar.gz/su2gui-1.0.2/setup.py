from setuptools import setup, find_packages

# Discover subpackages under su2gui-main (core, ui, installer, etc.)
_subpackages = find_packages(where="su2gui-main")
_packages = ["su2gui"] + [f"su2gui.{p}" for p in _subpackages]

setup(
    name="su2gui",
    version='1.0.2',
    description="SU2GUI is a Python-based GUI for SU2 simulation setup, execution, and analysis.",
    python_requires=">=3.10",
    package_dir={"su2gui": "su2gui-main"},
    packages=_packages,
    include_package_data=True,
    package_data={
        "su2gui": [
            "JsonSchema.json",
            "su2_validation_schema.json",
            "user/*.*",
            "img/*",
            "icons/*",
        ],
    },
    install_requires=[
        "jsonschema>=4.19.1",
        "pandas>=2.1.0",
        "trame>=3.2.0",
        "trame-client>=2.12.0",
        "trame-components>=2.2.0",
        "trame-markdown>=3.0.0",
        "trame-matplotlib>=2.0.0",
        "trame-server>=2.12.0",
        "trame-vtk>=2.5.0",
        "trame-vuetify>=2.3.0",
        "vtk>=9.2.0",
    ],
    entry_points={
        "console_scripts": [
            "SU2_GUI=su2gui.su2gui:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    license="GPL-3.0",
)
