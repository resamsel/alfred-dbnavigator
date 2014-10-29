#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path

from dbnav.sources import Source
from dbnav.postgresql import init_postgresql
from dbnav.sqlite import init_sqlite
from tests.mock import init_mock

def init_sources(dir):
    Source.sources = []
    init_mock()