from setuptools import setup, find_packages

setup(
    name='daily_funcs',
    version='0.1.21',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'tqdm'
    ],
    author='gouqi',
    author_email='1249224822@qq.com',
    description='daily tools for data science employee',
    license='MIT',
    keywords='daily tools for data science employee',
    url='https://github.com/gouqi/daily_tools'
)