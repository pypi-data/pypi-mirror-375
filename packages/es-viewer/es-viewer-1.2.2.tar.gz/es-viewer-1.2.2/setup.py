from setuptools import setup

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="es-viewer",
    version="1.2.2",
    author="isee15",
    author_email="meizhitu@gmail.com",
    description="A lightweight, cross-platform desktop GUI for Elasticsearch",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/isee15/es-viewer",
    py_modules=["es_gui"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Database :: Front-Ends",
        "Environment :: X11 Applications :: Qt",
    ],
    python_requires='>=3.6',
    install_requires=[
        "PyQt6",
        "requests",
        "urllib3",
    ],
    entry_points={
        "gui_scripts": [
            "es-viewer = es_gui:main",
        ],
    },
)
