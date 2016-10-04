import htmloutputparallel.version
import setuptools

setuptools.setup(
    name="nose-html-output-parallel",
    version=htmloutputparallel.version.__version__,
    author='Rui Li',
    author_email = 'rui.li.spam@gmail.com',
    description="Nose plugin to produce test results in html and works with parallel testing (--processes=N).",
    license="GNU GENERAL PUBLIC LICENSE, Version 3",
    url="https://github.com/ruivapps/htmloutputparallel",
    download_url='https://github.com/ruivapps/htmloutputparallel/tarball/1.3',
    packages=["htmloutputparallel"],
    package_dir={'htmloutputparallel':'htmloutputparallel'},
    package_data={'htmloutputparallel': ['templates/*.jinja2']},
    install_requires=['nose', 'Jinja2'],
    classifiers=[
        "Environment :: Console",
        "Topic :: Software Development :: Testing",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    entry_points={
        'nose.plugins.0.10': [
            'html-output = htmloutputparallel.htmloutputparallel:HtmlOutput'
        ]
    }
)
