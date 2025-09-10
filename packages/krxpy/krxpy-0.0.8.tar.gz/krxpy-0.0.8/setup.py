# find_packages
# https://setuptools.pypa.io/en/latest/setuptools.html#using-find-packages
# https://stackoverflow.com/questions/43253701/python-packaging-subdirectories-not-installed
from setuptools import setup, find_packages
from pathlib import Path
this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text()

setup(
    name    = 'krxpy',
    version = '0.0.8',
    license = 'MIT',
    description = "KRX Data Crawling ...",
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/YongBeomKim/krxpy',
    author = 'momukji lab',
    author_email = 'ybkim@momukji.com',
    keywords = ['krxpy'],
    python_requires = '>=3',
    include_package_data = True,
    package_data = {'': ['json/*.json']}, # 파일추가
    packages = find_packages(
        exclude = ['jupyter', 'backup', '.vscode', '.ipynb_checkpoints']
    ),
    install_requires=[
        'pytip',
        'pandas',
        'lxml',
        'tqdm',
        'requests',
        'chardet',
    ],
    classifiers=[
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
