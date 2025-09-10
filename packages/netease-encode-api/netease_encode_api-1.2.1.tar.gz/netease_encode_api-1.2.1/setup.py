from setuptools import setup, find_packages

setup(
    classifiers=[
        # 发展时期
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        "Development Status :: 5 - Production/Stable",
        # 开发的目标用户
        "Intended Audience :: Customer Service",
        "Intended Audience :: Developers",
        # "Intended Audience :: End Users/Desktop",
        # 属于什么类型
        "Topic :: Communications :: File Sharing",
        "Topic :: Internet",
        # 许可证信息
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        # 目标 Python 版本
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    name="netease_encode_api",
    version="1.2.0",
    description="网易云weapi解码和封装。",
    author="CooooldWind_",
    url="https://github.com/CooooldWind/netease_encode_api",
    packages=find_packages(),
    install_requires=[
        "pycryptodome",
        "requests",
        "pyqrcode",
    ],
    entry_points={
        # "console_scripts": [""]
    },
)
