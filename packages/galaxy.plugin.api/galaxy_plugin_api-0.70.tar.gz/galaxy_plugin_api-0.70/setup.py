from setuptools import setup, find_packages

setup(
    name="galaxy.plugin.api",
    version="0.70",
    description="GOG Galaxy Integrations Python API",
    author='Galaxy team',
    author_email='galaxy@gog.com',
    packages=find_packages("src"),
    package_dir={'': 'src'},
    python_requires="~=3.13.0",  # This package working with Python 3.13.x embedded in GOG Galaxy 2.0
    install_requires=[
        "aiohttp>=3.12.15",
        "certifi>=2025.8.3",
        "psutil>=5.6.6; sys_platform == 'darwin'"
    ]
)
