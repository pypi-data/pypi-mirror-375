 #python setup.py bdist_wheel

from setuptools import setup, find_packages

setup(
    name="itgeeker",
    version="0.1.0",
    packages=find_packages(exclude=["main.py"]),
    # 你可以根据需要添加更多配置项
    author="ITGeeker",
    description="ITGeeker Tools Package",
    python_requires=">=3.6",
)

from setuptools import setup, find_packages

setup(
    name='your_package_name',  # 替换为你的包名
    version='1.0.0',  # 替换为你的版本号
    packages=find_packages(),  # 自动查找所有包
    include_package_data=True,  # 包含额外的数据文件（如README.md，LICENSE等）
    install_requires=[  # 声明依赖的包
        'requests',
        'beautifulsoup4'
    ],
    entry_points={  # 可选：定义命令行入口
        'console_scripts': [
            'your_command = your_package.module:your_function'
        ]
    },
    #  可选：其他元数据，如作者、描述、许可证等
)