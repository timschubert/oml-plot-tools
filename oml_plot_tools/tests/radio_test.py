# -*- coding: utf-8 -*-

# pylint:disable=missing-docstring
import unittest

from . import common as test_common
from .. import consum

class TestTraj(unittest.TestCase):

    def test_doc(self):
        test_common.unittest_help_as_doc(self, consum)
