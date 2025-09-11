from setuptools import setup, find_packages

setup(
    name='xtrapnet',
    version='0.9.0',
    packages=find_packages(),
    install_requires=[
        'torch>=2.0.0', 
        'numpy>=1.21.0', 
        'scipy>=1.7.0',
        'scikit-learn>=1.0.0',
        'matplotlib>=3.5.0',
        'transformers>=4.20.0',
        'flask>=2.0.0',
        'pyyaml>=6.0',
        'psutil>=5.8.0'
    ],
    author='cykurd',
    author_email='cykurd@gmail.com',
    description='Novel framework for extrapolation control with Adaptive Uncertainty Decomposition, Constraint Satisfaction Networks, and Extrapolation-Aware Meta-Learning',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/cykurd/xtrapnet',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
