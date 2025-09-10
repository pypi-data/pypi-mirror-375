from setuptools import setup, find_packages
from pathlib import Path

setup(
    name='ytsage', 
    version='4.8.3',
    author='oop7',
    author_email='oop7_support@proton.me', 
    description='Modern YouTube downloader with a clean PySide6 interface.', 
    long_description=Path('README.md').read_text(encoding='utf-8'),
    long_description_content_type='text/markdown',
    url='https://github.com/oop7/YTSage',
    packages=find_packages(),
    keywords=['youtube', 'downloader', 'video', 'audio', 'PySide6', 'yt-dlp', 'GUI'],
    install_requires=[
        'yt-dlp',
        'PySide6',
        'requests',
        'Pillow',
        'packaging',
        'markdown',
        'pyglet',
        'loguru',
        'setuptools',
    ],
    include_package_data=True,
    package_data={
        'ytsage': [
            'assets/Icon/icon.png',  # Include the application icon
            'assets/sound/notification.mp3',  # Include the notification sound file
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Downloading',
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Utilities',
        'Environment :: X11 Applications :: Qt',
    ],
    python_requires='>=3.9',
    entry_points={
        'console_scripts': [
            'ytsage=ytsage.main:main',
        ],
    },
    project_urls={
        'Homepage': 'https://github.com/oop7/YTSage',
        'Bug Tracker': 'https://github.com/oop7/YTSage/issues',
        'Reddit': 'https://www.reddit.com/r/NO-N_A_M_E/',
    },
)