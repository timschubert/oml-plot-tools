#!/usr/bin/python
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


""" plot_oml_consum.py

plot oml filename node consumption
           [-abcehptv] -i <filename> or --input=<filename>

for time verification --time or -t
for begin sample --begin=<sample_beg> or -b <sample_beg>
for end sample --end=<sample_end> or -e <sample_end>
for label title plot --label=<title> or -l <title>
for plot consumption --power or -p
for plot voltage --voltage or -v
for plot current --current or -c
for all plot --all or -a
for help use --help or -h
"""


import sys
import getopt
import matplotlib.pyplot as plt
from . import common


MEASURES_D = common.measures_dict(
    ('power', float, 'Power (W)'),
    ('voltage', float, 'Voltage (V)'),
    ('current', float, 'Current (A)'),
)

def usage():
    """Usage command print """
    print __doc__


def oml_plot_conso(data, title, meas_tuples):
    """ Plot consumption value for 'meas_tuples'

    :param data: numpy array returned by oml_read
    :param title: Subplots title base
    :param meas_tuples: numpy.dtypesplots seperated on different windows
    """

    nbplots = len(meas_tuples)
    plt.figure()

    for num, meas in enumerate(meas_tuples, start=1):
        plt.subplot(nbplots, 1, num)

        _title = '%s %s' % (title, meas.name)
        common.plot(data, _title, meas.name, meas.label)


def main():
    """ Main command """
    options = []
    filename = ""
    try:
        opts, _ = getopt.getopt(sys.argv[1:], "i:htpcvab:e:l:",
                                ["input=", "help", "time", "power", "current",
                                 "voltage", "all", "begin=", "end=", "label="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    s_beg = 0
    s_end = -1
    title = "Node"
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-i", "--input"):
            filename = arg
        elif opt in ("-l", "--label"):
            title = arg
        elif opt in ("-b", "--begin"):
            s_beg = int(arg)
        elif opt in ("-e", "--end"):
            s_end = int(arg)
        elif opt in ("-t", "--time"):
            options.append("-t")
        elif opt in ("-p", "--power"):
            options.append("-p")
        elif opt in ("-c", "--current"):
            options.append("-c")
        elif opt in ("-v", "--voltage"):
            options.append('-v')
        elif opt in ("-a", "--all"):
            options.append("-a")

    if len(filename) == 0:
        usage()
        sys.exit(2)

    # Load file
    data = common.oml_load(filename, 'consumption', MEASURES_D.values())
    data = data[s_beg:s_end]

    if '-p' in options:
        oml_plot_conso(data, title, [MEASURES_D['power']])
    if "-v" in options:
        oml_plot_conso(data, title, [MEASURES_D['voltage']])
    if "-c" in options:
        oml_plot_conso(data, title, [MEASURES_D['current']])

    # All Plot on the same window
    if "-a" in options:
        oml_plot_conso(data, title, MEASURES_D.values())

    # Clock verification
    if "-t" in options:
        common.oml_plot_clock(data)

    plt.show()


if __name__ == "__main__":
    main()
