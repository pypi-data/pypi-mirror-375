from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Đọc các yêu cầu từ requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="tsearch",
    version="1.0.13",
    author="xakuyaya",
    description="Search Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tsearch",  # URL tới repo hoặc website
    packages=find_packages(),  # Tìm tất cả các package
    include_package_data=True,  # Bao gồm các file tĩnh
    install_requires=requirements,  # Sử dụng các thư viện từ requirements.txt
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
