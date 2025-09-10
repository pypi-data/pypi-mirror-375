import setuptools
import os

# Đọc README.md nếu có
readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
if os.path.exists(readme_path):
    with open(readme_path, encoding='utf-8') as f:
        long_description = f.read()
else:
    long_description = ''

# Đọc requirements.txt nếu có
req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
if os.path.exists(req_path):
    with open(req_path, encoding='utf-8') as f:
        requirements = f.read().splitlines()
else:
    requirements = []

setuptools.setup(
    name="tsearch",  # Đổi tên nếu muốn
    version="1.0.14",
    author="xakuyaya",
    author_email="your.email@example.com",
    description="Package for uploads folder",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/uploads-parent",  # Cập nhật nếu có repo
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    include_package_data=True,
)
