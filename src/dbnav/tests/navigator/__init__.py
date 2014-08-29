#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import unittest

from os import path
from dbnav.tests.generator import test_generator, params
from dbnav.tests.sources import init_sources
from dbnav import navigator

DIR = path.dirname(__file__)
TEST_CASES = map(lambda p: path.basename(p), glob.glob(path.join(DIR, 'resources/testcase-*')))

init_sources(DIR)

class OutputTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

def load_suite():
    command = 'dbnav'
    for tc in TEST_CASES:
        test_name = 'test_%s_%s' % (command, tc.replace('-', '_'))
        test = test_generator(navigator, command, DIR, tc, ['-t'])
        test.__doc__ = 'Params: "%s"' % params(DIR, tc)
        setattr(OutputTestCase, test_name, test)
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(OutputTestCase)
    return suite