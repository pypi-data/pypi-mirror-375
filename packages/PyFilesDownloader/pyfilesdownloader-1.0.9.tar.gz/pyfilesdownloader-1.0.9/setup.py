import setuptools

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name="PyFilesDownloader",
    version="1.0.9",
    keywords="一个下载文件的Python库",
    author="赤鸢仙人",
    author_email="2640610281@qq.com",
    description="一个下载文件的Python库",
    long_description=long_description,
    long_description_content_type='text/markdown',
    # license="AGPL-3.0",
    url="https://gitee.com/chiyaun/PyFilesDownloader",
    packages=setuptools.find_packages(),
    platforms=["all"],
    python_requires='>=3.7',
    install_requires=[
        "requests",
        "pycryptodome",
        "m3u8"
    ],
    extras_require={},
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
    ],
    project_urls={
        'Project Homepage': 'https://gitee.com/chiyaun/PyFilesDownloader',
        'Documentation': 'https://gitee.com/chiyaun/PyFilesDownloader/blob/master/README.md',
        'Source Code': 'https://gitee.com/chiyaun/PyFilesDownloader',
        'Bug Tracker': 'https://gitee.com/chiyaun/PyFilesDownloader/issues',
    }
)
# 打包命令
# python setup.py sdist build
# 上传命令
# twine upload dist/pyfilesdownloader-1.0.9.tar.gz
