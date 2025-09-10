from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

extensions = [
    Extension('quantum_sdk.core', ['quantum_sdk/core.py'])
]

setup(
    name='quantum-scoring-sdk',
    version='0.2.0',  # Nueva versión
    author='Jaime Alexander Jimenez Lozano',
    author_email='jaimeajl@hotmail.com',
    description='Quantum-native framework for business scoring and optimization',
    long_description=long_description,
    long_description_content_type='text/markdown',
    ext_modules=cythonize(extensions),
    packages=find_packages(),
    package_data={
        'quantum_sdk': ['*.pyd', '*.so'],
    },
    install_requires=[
        'numpy',
        'scikit-learn',
        'qiskit>=0.45.0',  # Solo simulador
        'qiskit-aer>=0.13.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires='>=3.8',
)
