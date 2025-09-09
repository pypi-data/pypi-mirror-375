from setuptools import setup, find_packages

setup(
    name='tibbtech',                     # Your package name
    version='0.1.2',
    packages=find_packages(),            # Automatically find all sub-packages
    install_requires=[],                 # Add dependencies here or in requirements.txt
    author='Tibbtech',
    author_email='taharazzaq091@gmail.com',
    description='Tibbtech codebase',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    # url='https://github.com/yourusername/mypackage',  # Optional
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
