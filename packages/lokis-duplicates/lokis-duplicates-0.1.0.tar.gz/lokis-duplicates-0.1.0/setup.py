from setuptools import setup, find_packages

setup(
    name="lokis-duplicates",  # 🔹 Package name on PyPI
    version="0.1.0",
    description="A Python library by Loki to find duplicate values in lists, strings, and more.",
    author="Lokeshwaran (Loki)",
    author_email="your-email@example.com",  # put your real email
    url="https://github.com/your-username/lokis-duplicates",  # optional GitHub repo
    packages=find_packages(),
    python_requires=">=3.6",
    license="MIT",
    keywords=["duplicates", "lokis", "find duplicates", "python"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
