from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

extensions = [
    Extension('quantum_sdk.core', ['quantum_sdk/core.py'])
]

setup(
    name='quantum-scoring-sdk',
    version='0.1.0',
    author='Jaime Alexander Jimenez Lozano',
    author_email='jaimeajl@hotmail.com',
    description='Framework universal para scoring y optimización de negocios',
    long_description=long_description,
    long_description_content_type='text/markdown',
    ext_modules=cythonize(extensions),
    packages=find_packages(),
    package_data={
        'quantum_sdk': ['*.pyd', '*.so'],
    },
    install_requires=['requests', 'numpy'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: Microsoft :: Windows",
        "Development Status :: 3 - Alpha",
    ],
    python_requires='>=3.8',
)
