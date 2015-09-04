# -*- coding: utf-8 -*-

# This file is a part of IoT-LAB oml-plot-tools
# Copyright (C) 2015 INRIA (Contact: admin@iot-lab.info)
# Contributor(s) : see AUTHORS file
#
# This software is governed by the CeCILL license under French law
# and abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# http://www.cecill.info.
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.


# pylint:disable=missing-docstring
import unittest

from .common import test_file_path, utest_help_as_doc, utest_plot_and_compare
from .. import consum


class TestConsumption(unittest.TestCase):

    def setUp(self):
        conso_file = test_file_path('examples', 'consumption.oml')
        self.data = consum.oml_load(conso_file)
        self.title = 'Node'

    def test_plot_all(self):
        ref_img = test_file_path('examples', 'consumption_all.png')
        consum.oml_plot(self.data, self.title, consum.MEASURES_D.values())

        utest_plot_and_compare(self, ref_img)

    def test_plot_current(self):
        ref_img = test_file_path('examples', 'consumption_current.png')
        consum.oml_plot(self.data, self.title, [consum.MEASURES_D['current']])
        utest_plot_and_compare(self, ref_img)

    def test_plot_clock(self):
        ref_img = test_file_path('examples', 'consumption_clock.png')
        consum.common.oml_plot_clock(self.data)
        utest_plot_and_compare(self, ref_img)


class TestDoc(unittest.TestCase):
    def test_doc(self):
        utest_help_as_doc(self, consum)
