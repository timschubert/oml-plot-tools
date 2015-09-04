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


""" plot_oml_radio.py

plot oml filename [-tbeaplh] -i <filename> or --input=<filename>

for time verification --time or -t
for begin sample --begin=<sample_beg> or -b <sample_beg>
for end sample --end=<sample_end> or -e <sample_end>
for label title plot --label=<title> or -l <title>
for plot in one window --all or -a
for plot in separate windows --plot or -p
for help use --help or -h
"""

# disabling pylint errors 'E1101' no-member, false positive from pylint
# pylint:disable=I0011,E1101

import sys
import getopt
import matplotlib.pyplot as plt
from . import common

MEASURES_D = common.measures_dict(
    ('channel', int, 'Channel'),
    ('rssi', int, 'RSSI (dBm)'),
)


def list_channels(data):
    """ List radio channels used in data """
    channels = list(set(data['channel']))
    return sorted(channels)


def with_channel(data, channel):
    """ Extract data where measured channel == `channel` """
    select = data['channel'] == channel
    return data[select]


def oml_plot_rssi(data, title, seperated=False):
    """ Plot rssi for all channels.

    :param data: numpy array returned by oml_read
    :param title: Subplots title base
    :param seperated: plots seperated on different windows
    """

    channels = list_channels(data)
    nbplots = len(channels)
    meas = MEASURES_D['rssi']

    # Only window for all
    if not seperated:
        plt.figure()

    for num, channel in enumerate(channels, start=1):
        # Select data for channel
        cdata = with_channel(data, channel)
        _title = '%s Channel %s' % (title, channel)

        # One window per plot
        if seperated:
            plt.figure()

        plt.subplot(nbplots, 1, num)
        common.plot(cdata, _title, meas.name, meas.label)


def usage():
    """ Usage command print """
    print __doc__


def main():  # pylint:disable=R0912
    """ Main command
    """
    options = []
    filename = ""
    try:
        opts, _ = getopt.getopt(sys.argv[1:], "i:htapb:e:l:",
                                ["input=", "help", "time", "all", "plot",
                                 "begin=", "end=", "label="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    s_beg = 0
    s_end = -1
    title = ""
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-i", "--input"):
            filename = arg
        elif opt in ("-l", "--label"):
            title = arg
        elif opt in ("-t", "--time"):
            options.append("-t")
        elif opt in ("-b", "--begin"):
            s_beg = int(arg)
        elif opt in ("-e", "--end"):
            s_end = int(arg)
        elif opt in ("-a", "--all"):
            options.append("-a")
        elif opt in ("-p", "--plot"):
            options.append("-p")

    if len(filename) == 0:
        usage()
        sys.exit(2)

    # Load file
    data = common.oml_load(filename, 'radio', MEASURES_D.values())
    data = data[s_beg:s_end]

    # Plot in a single window
    if '-a' in options:
        oml_plot_rssi(data, title)
    # Plot in several windows
    if '-p' in options:
        oml_plot_rssi(data, title, seperated=True)

    # Clock verification
    if '-t' in options:
        common.oml_plot_clock(data)
    plt.show()


if __name__ == "__main__":
    main()
