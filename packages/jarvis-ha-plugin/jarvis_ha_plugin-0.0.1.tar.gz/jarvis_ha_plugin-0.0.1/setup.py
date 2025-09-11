from setuptools import setup, find_packages

setup(
    name="jarvis_ha_plugin",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "requests>=2.32.3",
        "jarvis-api-library>=1.0.0",
    ],
    author="Samuel Lewis",
    description="This is a plugin that manages the interactions with Homeassistant.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown"
)