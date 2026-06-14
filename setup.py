from setuptools import setup, find_packages

setup(
    name="skill-for-manus-ai",
    version="1.0.0",
    description="Comprehensive skill collection for Manus AI with credit optimization",
    author="yehazkiell",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pyyaml>=6.0",
        "pydantic>=2.0",
        "tiktoken>=0.5.0",
    ],
    entry_points={
        "console_scripts": [
            "manus-skills=core.loader:main",
        ],
    },
)
