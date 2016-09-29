# Nose HTML Output Parallel (nose-html-output-parallel)
## Why another nose plugin
I really **need** HTML test report for my tests

I really **love** run nosetests in parallel (--processes=N)

After seaching and tried almost all nose html output plugin from pip, I found zero html output plugin works --processes=N.

Only options is write one myself. The output HTML is build from jinja2, so it's easy to modify template or user different template for different report. 

##Install
via PIP

```
pip install nose-html-output-parallel
```
via Download

```
python setup.py install
```

##Parameters 

Parameter | Environment Variable| Description | Required
---------|---------|--------|----------
--with-html-output | NOSE\_WITH\_HTML\_OUTPUT | enable html output plugin | YES
--html-out-file | NOSE\_HTML\_OUT\_FILE | set output filename. default is "results.html" | NO
--html-jinja-template| NOSE\_HTML\_JINJA\_TEMPLATE |use different jinja template instead default | NO
--html-out-title | NOSE\_HTML\_OUT\_TITLE | HTML title and header | NO

##Examples
Generate normal report to save results.html

```
nosetests --with-html-output
```
Generate report and save to mytest.html with 2 processes 

```
nosetests --with-html-output --html-out-file=mytest.html --processes=2
```
Generate report and save to test2.html and use /tmp/new_test.jinja template with 4 processes in parallel

```
nosetests --with-html-output --html-out-file=test2.html --html-jinja-tempalte=/tmp/new_test.jinja --processes=4
```

Generate report with html title/header = "Sunday Test" and save to sunday.html

```
nosetests --with-html-output --html-out-file=sunday.html --html-out-title="Sunday Test"
```

Generate report by using Environment Variables instead parameters

```
export NOSE_WITH_HTML_OUTPUT=true
export NOSE_HTML_OUT_FILE=mytest.html
export NOSE_HTML_JINJA_TEMPLATE=/tmp/test_template2.jinja
export NOSE_HTML_OUT_TITLE="Test by using Environment Variables"

nosetests 
```
 
##Thanks
* I learned how to use multiprocessing.Manager to work with nosetests parallel test from this project
	* <https://github.com/Ignas/nose_xunitmp>

* I download the jinja2 template from this project and use it to generate report 
	* <https://github.com/lysenkoivan/nose-html-reporting>


##Bugs
If you find one please report, otherwise you own it.

create pull request always works better 


