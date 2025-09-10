
from setuptools import setup, find_packages
import os

# Read the README file for long description
current_dir = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(os.path.dirname(current_dir), 'README.md')

long_description = "VietCardLib - Thư viện xử lý ORB, tiền xử lý và OCR giấy tờ tùy thân Việt Nam"
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()

setup(
    name='VietCardLib',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'VietCardLib': [
            'templates/base/*.jpg',
            'templates/base/*.png', 
            'templates/adjusted/*.jpg',
            'templates/adjusted/*.png',
            'data/*.db'
        ],
    },
    description='Thư viện xử lý ORB, tiền xử lý và OCR giấy tờ tùy thân Việt Nam',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Đoàn Ngọc Thành',
    author_email='dnt.doanngocthanh@gmail.com',
    url='https://github.com/doanngocthanh/VietCardLib',
    license='MIT',
    install_requires=[
        'opencv-python>=4.0.0',
        'numpy>=1.18.0',
        'matplotlib>=3.0.0',
        'scikit-image>=0.17.0',
        'Pillow>=8.0.0'
    ],
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'pytest-cov>=2.10.0',
            'black>=21.0.0',
            'flake8>=3.8.0',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Image Processing',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.7',
    keywords='orb opencv image-processing computer-vision vietnam-id card-recognition',
    project_urls={
        'Bug Reports': 'https://github.com/doanngocthanh/VietCardLib/issues',
        'Source': 'https://github.com/doanngocthanh/VietCardLib',
        'Documentation': 'https://github.com/doanngocthanh/VietCardLib/blob/main/README.md',
    },
)
