# __init__.py
"""
pip_name_generator: minimal package with a single public function to generate setup.py content.
"""
from typing import Optional

__all__ = ["generate_setup_py_from_metadata"]

def generate_setup_py_from_metadata(custom_text: str, author: Optional[str] = None) -> str:
    """
    Generate a parsable Python setup.py script as a string based on provided metadata.

    Args:
        custom_text: Non-empty description used for long_description and description.
        author: Optional; if provided and contains '@', treated as author_email; otherwise treated as author name.

    Returns:
        A string containing a minimal, valid Python file that calls setup(...)
    """
    if not isinstance(custom_text, str) or not custom_text.strip():
        raise ValueError("custom_text must be a non-empty string.")

    long_desc = custom_text.strip()
    package_name = "pip_name_generator_example"
    version = "0.1.0"

    lines = [
        "from setuptools import setup, find_packages",
        "",
        "setup(",
        f"    name='{package_name}',",
        f"    version='{version}',",
        f"    description={repr(long_desc[:100])},",
        f"    long_description={repr(long_desc)},",
        "    long_description_content_type='text/markdown',",
        "    packages=find_packages(),",
        "    include_package_data=True,",
    ]

    if author:
        if "@" in author:
            lines.append(f"    author_email={repr(author)},")
        else:
            lines.append(f"    author={repr(author)},")
    lines.append(")")
    return "\n".join(lines)