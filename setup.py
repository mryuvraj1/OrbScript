from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="orbscript",
    version="1.0.0",
    author="OrbScript Developer",
    description="A custom programming language for automation and bots",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/orbscript",
    py_modules=[
        "lexer",
        "parser", 
        "ast",
        "compiler",
        "bytecode",
        "vm",
        "main"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "orbscript=main:main",
        ],
    },
)