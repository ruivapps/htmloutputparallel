import codecs
import doctest
import os
import sys
import traceback
import re
import inspect
import StringIO
import time
import datetime
import multiprocessing
import collections

import jinja2

from nose.plugins.base import Plugin
from nose.exc import SkipTest
from nose.pyversion import force_unicode, format_exception

def id_split(idval):
    m = re.match(r'^(.*?)(\(.*\))$', idval)
    if m:
        name, fargs = m.groups()
        head, tail = name.rsplit(".", 1)
        return [head, tail+fargs]
    else:
        return idval.rsplit(".", 1)

def nice_classname(obj):
    """Returns a nice name for class object or class instance.

        >>> nice_classname(Exception()) # doctest: +ELLIPSIS
        '...Exception'
        >>> nice_classname(Exception) # doctest: +ELLIPSIS
        '...Exception'

    """
    if inspect.isclass(obj):
        cls_name = obj.__name__
    else:
        cls_name = obj.__class__.__name__
    mod = inspect.getmodule(obj)
    if mod:
        name = mod.__name__
        # jython
        if name.startswith('org.python.core.'):
            name = name[len('org.python.core.'):]
        return "%s.%s" % (name, cls_name)
    else:
        return cls_name

def exc_message(exc_info):
    """Return the exception's message."""
    exc = exc_info[1]
    if exc is None:
        # str exception
        result = exc_info[0]
    else:
        try:
            result = str(exc)
        except UnicodeEncodeError:
            try:
                result = unicode(exc)
            except UnicodeError:
                # Fallback to args as neither str nor
                # unicode(Exception(u'\xe6')) work in Python < 2.6
                result = exc.args[0]
    result = force_unicode(result, 'UTF-8')
    return result

class Tee(object):
    """used for stdout and stderr capture
    """
    def __init__(self, encoding, *args):
        self._encoding = encoding
        self._streams = args

    def write(self, data):
        data = force_unicode(data, self._encoding)
        for s in self._streams:
            s.write(data)

    def writelines(self, lines):
        for line in lines:
            self.write(line)

    def flush(self):
        for s in self._streams:
            s.flush()

    def isatty(self):
        return False


class HtmlOutput(Plugin):
    """This plugin provides test results in html format and works with parallel test."""
    name = 'html-output'
    score = 2000 #not really sure what's score
    encoding = 'UTF-8'
    error_report_file = None

    def __init__(self):
        super(HtmlOutput, self).__init__()
        self._capture_stack = []
        self._currentStdout = None
        self._currentStderr = None

    def _timeTaken(self):
        if hasattr(self, '_timer'):
            taken = time.time() - self._timer
        else:
            # test died before it ran (probably error in setup())
            # or success/failure added before test started probably
            # due to custom TestResult munging
            taken = 0.0
        return taken

    def options(self, parser, env):
        """Sets additional command line options."""
        Plugin.options(self, parser, env)
        parser.add_option("--html-out-file", action="store",
                default=env.get('NOSE_HTML_OUT_FILE', 'results.html'),
                dest="html_file",
                metavar="FILE",
                help="Produce results in the specified HTML file."
                "[NOSE_HTML_OUT_FILE]" )
        parser.add_option("--html-out-title", action="store",
                default=env.get('NOSE_HTML_OUT_TITLE', 'Unittest Report'),
                dest="html_title",
                help="The Title of the report in HTML"
                "[NOSE_HTML_OUT_TITLE]" )
        parser.add_option("--html-jinja-template", action="store",
                default=env.get('NOSE_HTML_JINJA_TEMPLATE', os.path.join(os.path.dirname(__file__), "templates", "report.jinja2")),
                dest="html_template", metavar="FILE",
                help="jinja2 template file"
                "[NOSE_HTML_JINJA_TEMPLATE]" )


    def configure(self, options, config):
        """Configures the html-xxx plugin."""
        super(HtmlOutput, self).configure(options, config)
        Plugin.configure(self, options, config)
        self.config = config
        if options.html_file:
            self.html_file = options.html_file
        if options.html_title:
            self.html_title=options.html_title
        if self.enabled:
            self.start_time=datetime.datetime.utcnow()
            self.jinja = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(options.html_template)),
                    trim_blocks=True, lstrip_blocks=True)
            self.jinja_template=options.html_template
            if not hasattr(self.config, '_nose_html_output_state'):
                manager = multiprocessing.Manager()
                self.errorlist=manager.list()
                self.stats = manager.dict(**{
                    'errors': 0,
                    'failures': 0,
                    'passes': 0,
                    'skipped': 0
                    })
                self.config._nose_html_output_state = self.errorlist, self.stats
            else:
                self.errorlist, self.stats = self.config._nose_html_output_state
            self.error_report_file_name = os.path.realpath(options.html_file)
            self.html_file_name = options.html_file

    def report(self, stream):
        """Writes an HTML output file (using some template?)
        """
        self.error_report_file = codecs.open(self.error_report_file_name, 'w',
                                             self.encoding, 'replace')
        self.stats['encoding'] = self.encoding
        self.stats['testsuite_name'] = self.html_file_name
        self.stats['total'] = (self.stats['errors'] + self.stats['failures']
                               + self.stats['passes'] + self.stats['skipped'])
        #craft data for jinja
        '''
        data = {
            classname: {
                stats : {
                    failures: int,
                    errors: int,
                    skipped: int,
                    passes: int,
                    total: int,
                },
                tests: [
                {
                    failed: boolean,
                    name: string,
                    type: string,  #passes|failures|error|skipped
                    shortDescription: string,
                    time: string,
                    stdout: string, #optional
                    message: string, #optional
                    tb: string, #optional
                },
                {
                    ...
                },
            classname: {
                ...
            }
        '''

        #sort all class names
        classes=[x['class'] for x in self.errorlist]
        class_stats={'failures':0, 'errors':0, 'skipped':0, 'passes':0, 'total':0}
        classes.sort()
        report_jinja=collections.OrderedDict()
        for _class_ in classes:
            report_jinja.setdefault(_class_, {})
            _class_stats_=class_stats.copy()
            for _error_ in self.errorlist:
                if _class_ != _error_['class']:
                    continue
                report_jinja[_class_].setdefault('tests', [])
                if _error_ not in report_jinja[_class_]['tests']:
                    report_jinja[_class_]['tests'].append(_error_)
                _class_stats_[_error_['type']]+=1
            _class_stats_['total']=sum(_class_stats_.values())
            report_jinja[_class_]['stats']=_class_stats_

        end_time=datetime.datetime.utcnow()
        self.error_report_file.write(self.jinja.get_template(os.path.basename(self.jinja_template)).render(
            html_title=self.html_title,
            report = report_jinja,
            stats = self.stats,
            start_time = str(self.start_time),
            duration = str(datetime.datetime.utcnow()-self.start_time),
            ))
        self.error_report_file.close()
        if self.config.verbosity > 1:
            stream.writeln("-" * 70)
            stream.writeln("HTML: %s" % self.error_report_file.name)

    def _startCapture(self):
        self._capture_stack.append((sys.stdout, sys.stderr))
        self._currentStdout = StringIO.StringIO()
        self._currentStderr = StringIO.StringIO()
        sys.stdout = Tee(self.encoding, self._currentStdout, sys.stdout)
        sys.stderr = Tee(self.encoding, self._currentStderr, sys.stderr)

    def startContext(self, context):
        self._startCapture()

    def stopContext(self, context):
        self._endCapture()

    def beforeTest(self, test):
        """Initializes a timer before starting a test."""
        self._timer = time.time()
        self._startCapture()

    def _endCapture(self):
        if self._capture_stack:
            sys.stdout, sys.stderr = self._capture_stack.pop()

    def afterTest(self, test):
        self._endCapture()
        self._currentStdout = None
        self._currentStderr = None

    def finalize(self, test):
        while self._capture_stack:
            self._endCapture()

    def _getCapturedStdout(self):
        if self._currentStdout:
            value = self._currentStdout.getvalue()
            if value:
                return value
        return ''

    def _getCapturedStderr(self):
        if self._currentStderr:
            value = self._currentStderr.getvalue()
            if value:
                return value
        return ''

    def addError(self, test, err, capt=None):
        """Add error output to Xunit report.
        """
        taken = self._timeTaken()

        if issubclass(err[0], SkipTest):
            _type = 'skipped'
            self.stats['skipped'] += 1
        else:
            _type = 'errors'
            self.stats['errors'] += 1

        tb = format_exception(err, self.encoding)
        _id = test.id()

        self.errorlist.append( {
            'failed': True,
            'class': id_split(_id)[0],
            'name': id_split(_id)[-1],
            'time': str(datetime.timedelta(seconds=taken)),
            'type': _type,
            'exception': nice_classname(err[0]),
            'message': exc_message(err),
            'tb': tb,
            'stdout': self._getCapturedStdout(),
            'stderr': self._getCapturedStderr(),
            'shortDescription': test.shortDescription(),
            })

    def addFailure(self, test, err, capt=None, tb_info=None):
        """Add failure output to Xunit report.
        """
        taken = self._timeTaken()
        tb = format_exception(err, self.encoding)
        self.stats['failures'] += 1
        _id = test.id()

        self.errorlist.append({
            'failed': True,
            'class': id_split(_id)[0],
            'name': id_split(_id)[-1],
            'time': str(datetime.timedelta(seconds=taken)),
            'type': 'failures',
            'exception': nice_classname(err[0]),
            'message': exc_message(err),
            'tb': '', #do not display traceback on failure
            'stdout': self._getCapturedStdout(),
            'stderr': self._getCapturedStderr(),
            'shortDescription': test.shortDescription(),
            })

    def addSuccess(self, test, capt=None):
        """Add success output to Xunit report.
        """
        taken = self._timeTaken()
        self.stats['passes'] += 1
        _id = test.id()
        self.errorlist.append({
            'failed': False,
            'class': id_split(_id)[0],
            'name': id_split(_id)[-1],
            'time': str(datetime.timedelta(seconds=taken)),
            'type' : 'passes',
            'exception': '',
            'stdout': self._getCapturedStdout(),
            'stderr': self._getCapturedStderr(),
            'shortDescription': test.shortDescription(),
            })
