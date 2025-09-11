from setuptools import setup, find_packages

setup(
    # Basic info
    name='network_spatial_coherence',
    version='0.1.1996',
    author='David Fernandez Bonet',
    author_email='dfb@kth.se',
    url='https://github.com/DavidFernandezBonet/Spatial Constant Analysis',
    description='Network Validation using the Spatial Coherence Framework.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',  # This is important for markdown to render correctly


    # Package info
    packages=find_packages(exclude=('tests', 'docs')),  # Automatically find and include all packages
    install_requires=[
        'matplotlib',
        'memory_profiler==0.61.0',
        'networkx',
        'nodevectors',
        'numpy',
        'pandas',
        'pecanpy',
        'Pillow==10.2.0',  
        'igraph',
        'scienceplots==2.1.1',
        'scikit_learn',
        'scipy',
        'seaborn',
        'umap-learn',
        'statsmodels',
    ],



	package_data={
	    'network_spatial_coherence': [
		'docs/build/html/**/*',  # Use glob pattern to include all files and subdirectories
		'example_edge_list.pickle',
		'dna_cool2.png',
		'edge_list_us_counties.csv',
		'edge_list_weighted.csv',
	    ],
	},
	include_package_data=True,

    # Additional metadata
    classifiers=[
        'Development Status :: 3 - Alpha',  # Change as appropriate
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',  # Change as appropriate
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    # Additional requirements
    python_requires=">=3.8,<=3.12",
    extras_require={
        'dev': [
            'pytest>=3.7',
            'check-manifest',
            'twine',
            # etc.
        ],
    },
)
