from setuptools import setup


setup(
        packages=['models', 'database', 'repository', 'tools'],
        tests_require=['pytest'],
        name='gyresources',
        test_suite='tests'
        )
