from setuptools import setup, find_packages

setup(
    name="smart-commit",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "google-generativeai",
        "python-dotenv",
        "pydantic",
        "pyyaml",
    ],
    entry_points={
        "console_scripts": [
            "smart-commit=smart_commit.main:main",
        ],
    },
    python_requires=">=3.7",
    description="AI-powered commit message generator",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/smart-commit",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
