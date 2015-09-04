# -*- coding:utf-8 -*-

""" Common tests functions """

import sys
import mock
from cStringIO import StringIO


def help_main_and_doc(module, help_opt='--help'):
    """ Check that help message is module docstring """

    if not hasattr(module, 'main'):
        return None, None

    help_args = [module.__name__, help_opt]
    out_msg = StringIO()

    with mock.patch.object(sys, 'argv', help_args):
        with mock.patch.object(sys, 'stderr', out_msg):
            with mock.patch.object(sys, 'stdout', out_msg):
                try:
                    module.main()
                except SystemExit:
                    pass

    help_msg = out_msg.getvalue().strip()
    help_doc = module.__doc__.strip()
    print help_msg
    print help_doc

    return help_msg, help_doc


def unittest_help_as_doc(unittest_instance, module, *args, **kwargs):
    """ Run help_as_doc as unittest test """
    help_msg, help_doc = help_main_and_doc(module, *args, **kwargs)
    unittest_instance.assertEqual(help_msg, help_doc)
