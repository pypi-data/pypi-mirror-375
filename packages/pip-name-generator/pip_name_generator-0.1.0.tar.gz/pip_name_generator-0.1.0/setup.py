from pathlib import Path
from setuptools import setup, find_packages

def _read_long_description() -> str:
    readme = Path(__file__).with_name("README.md")
    if readme.exists():
        try:
            return readme.read_text(encoding="utf-8")
        except Exception:
            return ""
    return ""

long_description = _read_long_description().strip()

setup(
    name="pip_name_generator",
    version="0.1.0",
    author="Eugene Evstafev",
    author_email="hi@eugene.plus",
    description="Minimal package with a single public function to generate setup.py content.",
    long_description=long_description or "A minimal package that provides a helper to generate a setup.py script content.",
    long_description_content_type="text/markdown",
    url="https://github.com/chigwell/pip_name_generator",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    license="MIT",
)