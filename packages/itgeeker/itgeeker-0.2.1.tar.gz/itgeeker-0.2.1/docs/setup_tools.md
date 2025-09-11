setuptools重点在于setup.py文件编写：https://docs.python.org/3.6/distutils/introduction.html#distutils-simple-example
# setup.py参数介绍：

name : 打包起来的包的文件名
version : 版本号,添加为打包文件的后缀名
author : 作者
author_email : 作者的邮箱
py_modules : 打包的.py文件
packages: 打包的python文件夹
include_package_data : 项目里会有一些非py文件,比如html和js等,这时候就要靠include_package_data 和 package_data 来指定了。package_data:一般写成{‘your_package_name’: [“files”]}, include_package_data还没完,还需要修改MANIFEST.in文件.MANIFEST.in文件的语法为: include xxx/xxx/xxx/.ini/(所有以.ini结尾的文件,也可以直接指定文件名)
license : 支持的开源协议
description : 对项目简短的一个形容
ext_modules : 是一个包含Extension实例的列表,Extension的定义也有一些参数。
ext_package : 定义extension的相对路径
requires : 定义依赖哪些模块
provides : 定义可以为哪些模块提供依赖
data_files :指定其他的一些文件(如配置文件),规定了哪些文件被安装到哪些目录中。如果目录名是相对路径,则是相对于sys.prefix或sys.exec_prefix的路径。如果没有提供模板,会被添加到MANIFEST文件中。
————————————————

                            版权声明：本文为博主原创文章，遵循 CC 4.0 BY-SA 版权协议，转载请附上原文出处链接和本声明。
                        
原文链接：https://blog.csdn.net/winycg/article/details/80025432

打开终端，定位到该文件夹下，输入：

python setup.py sdist

此时在目录中生成dist文件夹，文件夹中有testpg-1.0.tar.gz文件，用户安装的话只需要testpg-1.0.tar.gz文件即可。将此文件解压得到testpg-1.0文件夹，会发现该文件夹有我们刚刚书写的3个py文件，还有一个PKG-INFO，打开该文件，会显示该模块的具体信息：由于我们没有设置，所以为UNKOWN


```py
from setuptools import setup

setup(name='pagtest',
      version='1.0.0',
      description='A print test for PyPI',
      author='winycg',
      author_email='win@163.com',
      url='https://www.python.org/',
      license='MIT',
      keywords='ga nn',
      project_urls={
            'Documentation': 'https://packaging.python.org/tutorials/distributing-packages/',
            'Funding': 'https://donate.pypi.org',
            'Source': 'https://github.com/pypa/sampleproject/',
            'Tracker': 'https://github.com/pypa/sampleproject/issues',
      },
      packages=['pagtest'],
      install_requires=['numpy>=1.14', 'tensorflow>=1.7'],
      python_requires='>=3'
     )
```

