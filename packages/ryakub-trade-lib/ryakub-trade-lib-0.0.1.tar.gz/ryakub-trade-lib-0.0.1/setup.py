from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()

setup(
    name='ryakub-trade-lib',
    version='0.0.1',
    author='ryakub',
    author_email='yakubovsky.rom@yandex.ru',
    description='Библиотека для биржевой торговли MOEX',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='',
    packages=find_packages(),
    install_requires=['requests>=2.32.5', 'pyarrow==21.0.0', 'boto3==1.40.22', 'pandas==2.3.2'],
    classifiers=[
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='ryakub',
    project_urls={
        'GitHub': 'https://github.com/ryakub01'
    },
    python_requires='>=3.6'
)
