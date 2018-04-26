"""
Example setup file
"""

import setuptools


if __name__ == "__main__":
    setuptools.setup(
        name='off_psi4',
        version="0.0.1",
        description='Quantum mechanical calculations for Open Force Field project',
        author='Victoria Lim',
        author_email='limvt@uci.edu',
        url="https://github.com/vtlim/off_psi4",
        license='MIT',
        packages=setuptools.find_packages(),
        install_requires=[
            'numpy>=1.7',
        ],
        extras_require={
            'tests': [
                'pytest',
                'pytest-cov',
                'pytest-pep8',
                'tox',
            ],
        },

        tests_require=[
            'pytest',
            'pytest-cov',
            'pytest-pep8',
            'tox',
        ],

        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
        ],
        zip_safe=True,
    )
