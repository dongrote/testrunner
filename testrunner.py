#!/usr/bin/env python
from coverage import coverage
from optparse import OptionParser
import unittest
import inspect
import sys

threshold = 99.

def isTestModule(name,obj):
    if inspect.ismodule(obj):
        return name.startswith('test_')
    return False

def isTestSuite(obj):
    if inspect.isclass(obj):
        return issubclass(obj,unittest.TestSuite)
    return False

def isTestCase(obj):
    if inspect.isclass(obj):
        return issubclass(obj,unittest.TestCase)
    return False

def GetTestSuitesFromModule(mod):
    suites = []
    for name,obj in inspect.getmembers(mod):
        if isTestSuite(obj):
            suites.append(obj)
    return suites

def GetTestCasesFromModule(mod):
    cases = []
    for name,obj in inspect.getmembers(mod):
        if isTestCase(obj):
            cases.append(obj)
    return cases

def runTestsFromModuleWithName(mod,name):
    results = []
    testRunner = unittest.TextTestRunner(verbosity=2)
    testSuites = GetTestSuitesFromModule(mod)
    testCases = GetTestCasesFromModule(mod)
    for suite in testSuites:
        print 'Running tests in "%s.%s"' % (name,suite.__name__)
        results.append(testRunner.run(suite()))
    for case in testCases:
        print 'Running tests in "%s.%s"' % (name,case.__name__)
        results.append(testRunner.run(unittest.loader.makeSuite(case)))
    return results

def main():
    global threshold
    parser = OptionParser()
    parser.set_usage("Usage: %prog [options]")
    parser.add_option('-t','--threshold', dest='threshold', default=90,
        help='Set code coverage threshold [0-100]')
    (options,args) = parser.parse_args()
    threshold = float(int(options.threshold))
    if not 0. <= threshold <= 100.:
        print >> sys.stderr, 'Threshold %f outside of range [0.0-100.0]' % threshold
        sys.exit(-10)
    exit_val = 0
    cov = coverage(cover_pylib=False,omit=['/usr*','tests*',sys.modules[__name__].__file__])
    cov.start()
    import tests
    for name, obj in inspect.getmembers(tests):
        if isTestModule(name,obj):
            results = runTestsFromModuleWithName(obj,name)
            for result in results:
                if result.failures > 0:
                    exit_val = -1
                if result.errors > 0:
                    exit_val = -1
    cov.stop()
    cov.save()
    ccov = cov.report()
    cov.html_report()
    if ccov < threshold:
        print >> sys.stderr, 'Code coverage threshold not met: %d%% < %d%%' % (int(ccov+0.5),int(threshold))
        exit_val = -2
    else:
        print >> sys.stderr, 'Code coverage: %d%%; threshold set at %d%%' % (int(ccov+0.5),int(threshold))
    sys.exit(exit_val)

if '__main__' == __name__:
    main()
