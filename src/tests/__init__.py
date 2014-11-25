#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from tests import navigator, grapher, exporter, differ
from tests import utils, comment, querybuilder


def load_suite():
    suite = unittest.TestSuite()

    suite.addTest(utils.load_suite())
    suite.addTest(comment.load_suite())
    suite.addTest(querybuilder.load_suite())

    suite.addTest(navigator.load_suite())
    suite.addTest(grapher.load_suite())
    suite.addTest(exporter.load_suite())
    suite.addTest(differ.load_suite())

    return suite
