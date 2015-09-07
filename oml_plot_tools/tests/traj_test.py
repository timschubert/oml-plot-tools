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

from .common import utest_help_as_doc, utest_plot_and_compare, test_file_path
from .. import traj, common


class TestTrajectory(unittest.TestCase):
    def setUp(self):
        robot_file = test_file_path('examples', 'robot.oml')
        map_file = test_file_path('examples', 'grenoble-map.txt')
        circuit_file = test_file_path('examples', 'Jhall_w.json')

        self.data = traj.oml_load(robot_file)
        self.decos, self.img_map = traj.maps_load(map_file)
        self.circuit = traj.circuit_load(circuit_file)
        self.title = "Robot"

    def test_plot_all(self):
        ref_img = test_file_path('examples', 'trajectory_all.png')
        traj.oml_plot_map(self.data, self.title, self.decos,
                          self.img_map, self.circuit)
        utest_plot_and_compare(self, ref_img, 38)

    def test_plot_angle(self):
        ref_img = test_file_path('examples', 'trajectory_angle.png')
        traj.oml_plot_angle(self.data, self.title)
        utest_plot_and_compare(self, ref_img, 26)

    def test_plot_clock(self):
        ref_img = test_file_path('examples', 'trajectory_clock.png')
        common.oml_plot_clock(self.data)
        utest_plot_and_compare(self, ref_img, 29)


class TestDoc(unittest.TestCase):
    def test_doc(self):
        utest_help_as_doc(self, traj)
