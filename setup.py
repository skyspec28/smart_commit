from setuptools import setup, find_packages
import os


def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "AI-powered git commit message generator using Google's Gemini AI"


def get_version():
    about = {}
    with open(os.path.join("smart_commit", "__init__.py"), "r") as f:
        exec(f.read(), about)
    return about["__version__"]


setup(
    name="smart-commit",
    version=get_version(),
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "smart_commit": ["config.yml"],
    },
    install_requires=[
        "click>=8.0.0",
        "google-generativeai>=0.8.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "smart-commit=smart_commit.main:main",
        ],
    },
    python_requires=">=3.8",
    description="AI-powered git commit message generator using Google's Gemini AI",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    license="MIT",
    author="skyspec28",
    author_email="smart-commit@example.com",
    url="https://github.com/skyspec28/smart_commit",
    keywords="git, commit, ai, gemini, conventional-commits, automation",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    project_urls={
        "Bug Reports": "https://github.com/skyspec28/smart_commit/issues",
        "Source": "https://github.com/skyspec28/smart_commit",
        "Documentation": "https://github.com/skyspec28/smart_commit#readme",
    },
)
