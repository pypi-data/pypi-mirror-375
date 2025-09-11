import setuptools

# Read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setuptools.setup(
    name="git-lfs-advisor-cli",
    version="0.1.0",
    author="taicaile",
    author_email="",
    # A short, one-sentence summary of the package
    description="A script to find large/binary files and generate Git LFS commands.",
    # A long description read from the README.md file
    long_description=long_description,
    long_description_content_type='text/markdown',  # Important for rendering on PyPI
    url="https://github.com/taicaile/git-lfs-advisor",  # Replace with your project's URL
    # Use a standard src layout to find the package
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    python_requires='>=3.6',
    # List of dependencies required by your package
    install_requires=[
        # e.g., 'requests>=2.20.0',
    ],
    project_urls={
        "Bug Tracker": "https://github.com/taicaile/git-lfs-advisor/issues",
        "Source Code": "https://github.com/taicaile/git-lfs-advisor",
    },
    # Define the command-line entry point
    entry_points={
        'console_scripts': [
            # This creates a command 'git-lfs-advisor' that executes the main() function
            # in the 'cli.py' module within our 'get_lfs_advisor_cli' package.
            'git-lfs-advisor=get_lfs_advisor_cli.cli:main',
        ],
    },
)
