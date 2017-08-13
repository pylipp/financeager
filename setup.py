from setuptools import setup, find_packages

setup(
        name="financeager",
        version="1.0",
        description="Command line tool to administer finances",
        url="http://github.com/pylipp/financeager",
        author="Philipp Metzner",
        author_email="beth.aleph@yahoo.de",
        license="GPLv3",
        #classifiers=[],
        packages=find_packages(exclude=["test", "doc"]),
        entry_points = {
            "console_scripts": ["financeager = financeager.cli:main"]
            },
        install_requires=[]
        )
