from setuptools import setup, find_packages

with open('description_info.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='gj_unitrad',  # 你的包名
    version='0.1.35',  # 版本号
    description='unitrad打包',  # 包的简要描述
    long_description=long_description,  # 包的详细描述
    long_description_content_type='text/markdown',  # 描述文件的类型
    include_package_data=True,  # 包含包数据
    package_data={'gj_unitrad': ['*.py']},  # 指定数据文件
    author='yanli',  # 作者姓名
    author_email='1498046515@qq.com',  # 作者邮箱
    packages=find_packages(),  # 自动查找包目录
    python_requires='>3.9',  # python版本要求
    install_requires=[
        'pyyaml==6.0.2',
        'aiohttp==3.11.10',
        'pandas==2.0.0',
        'matplotlib==3.9.3',
        'Pillow==10.4.0'
    ],  # 依赖库列表 (除开python自带的包外的其他依赖库(代码中如果缺少了对应的库会导致无法运行的包))
)
