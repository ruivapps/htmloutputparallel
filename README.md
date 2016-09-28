# HTML Output Parallel (htmloutputparallel)
## Why another nose plugin
I really **need** the HTML test report

I really **like** run nose test in parallel (--processes=N)

After seaching and trying all nose html output plugin from pip, I found zero plugin I can use with nose --processes=N.

So I dicide to write one myself. The output HTML is build on from jinja2, so it's easy to modify the template or user totally different template for different report. 

##Install
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
 
##Todo
once I figure out how, I will try to put it on pip. so installation would be easier 

##Bugs
if you find any, please let me know. create pull request even better 


