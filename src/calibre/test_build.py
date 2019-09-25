#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'

'''
Test a binary calibre build to ensure that all needed binary images/libraries have loaded.
'''

import os, ctypes, sys, unittest, time

from calibre.constants import plugins, iswindows, islinux, isosx, ispy3
from polyglot.builtins import iteritems, map, unicode_type

is_ci = os.environ.get('CI', '').lower() == 'true'


class BuildTest(unittest.TestCase):

    @unittest.skipUnless(iswindows and not is_ci, 'DLL loading needs testing only on windows (non-continuous integration)')
    def test_dlls(self):
        import win32api
        base = win32api.GetDllDirectory()
        for x in os.listdir(base):
            if x.lower().endswith('.dll'):
                try:
                    ctypes.WinDLL(str(os.path.join(base, x)))
                except Exception as err:
                    self.assertTrue(False, 'Failed to load DLL %s with error: %s' % (x, err))

    @unittest.skipUnless(islinux, 'DBUS only used on linux')
    def test_dbus(self):
        import dbus
        if 'DBUS_SESSION_BUS_ADDRESS' in os.environ:
            bus = dbus.SystemBus()
            self.assertTrue(bus.list_names(), 'Failed to list names on the system bus')
            bus = dbus.SessionBus()
            self.assertTrue(bus.list_names(), 'Failed to list names on the session bus')
            del bus

    def test_regex(self):
        import regex
        self.assertEqual(regex.findall(r'(?i)(a)(b)', 'ab cd AB 1a1b'), [('a', 'b'), ('A', 'B')])
        self.assertEqual(regex.escape('a b', literal_spaces=True), 'a b')

    def test_chardet(self):
        from chardet import detect
        raw = 'mūsi Füße'.encode('utf-8')
        data = detect(raw)
        self.assertEqual(data['encoding'], 'utf-8')
        self.assertGreater(data['confidence'], 0.5)
        # The following is used by html5lib
        from chardet.universaldetector import UniversalDetector
        detector = UniversalDetector()
        self.assertTrue(hasattr(detector, 'done'))
        detector.feed(raw)
        detector.close()
        self.assertEqual(detector.result['encoding'], 'utf-8')

    def test_html5lib(self):
        import html5lib.html5parser  # noqa
        from html5lib import parse  # noqa

    def test_html5_parser(self):
        from html5_parser import parse
        parse('<p>xxx')

    def test_bs4(self):
        import soupsieve, bs4
        del soupsieve, bs4

    def test_lxml(self):
        from calibre.utils.cleantext import test_clean_xml_chars
        test_clean_xml_chars()
        from lxml import etree
        raw = b'<a/>'
        root = etree.fromstring(raw)
        self.assertEqual(etree.tostring(root), raw)

    def test_msgpack(self):
        from calibre.utils.serialize import msgpack_dumps, msgpack_loads
        from calibre.utils.date import utcnow
        for obj in ({1:1}, utcnow()):
            s = msgpack_dumps(obj)
            self.assertEqual(obj, msgpack_loads(s))
        self.assertEqual(type(msgpack_loads(msgpack_dumps(b'b'))), bytes)
        self.assertEqual(type(msgpack_loads(msgpack_dumps(u'b'))), unicode_type)
        large = b'x' * (100 * 1024 * 1024)
        msgpack_loads(msgpack_dumps(large))

    def test_imaging(self):
        from PIL import Image
        try:
            import _imaging, _imagingmath, _imagingft
            _imaging, _imagingmath, _imagingft
        except ImportError:
            from PIL import _imaging, _imagingmath, _imagingft
        _imaging, _imagingmath, _imagingft
        i = Image.open(I('lt.png', allow_user_override=False))
        self.assertGreaterEqual(i.size, (20, 20))

    def test_tinycss_tokenizer(self):
        from tinycss.tokenizer import c_tokenize_flat
        self.assertIsNotNone(c_tokenize_flat, 'tinycss C tokenizer not loaded')

    @unittest.skipUnless(getattr(sys, 'frozen', False), 'Only makes sense to test executables in frozen builds')
    def test_executables(self):
        from calibre.utils.ipc.launch import Worker
        from calibre.ebooks.pdf.pdftohtml import PDFTOHTML
        w = Worker({})
        self.assertTrue(os.path.exists(w.executable), 'calibre-parallel (%s) does not exist' % w.executable)
        self.assertTrue(os.path.exists(w.gui_executable), 'calibre-parallel-gui (%s) does not exist' % w.gui_executable)
        self.assertTrue(os.path.exists(PDFTOHTML), 'pdftohtml (%s) does not exist' % PDFTOHTML)
        if iswindows:
            from calibre.devices.usbms.device import eject_exe
            self.assertTrue(os.path.exists(eject_exe()), 'calibre-eject.exe (%s) does not exist' % eject_exe())

def find_tests():
    ans = unittest.defaultTestLoader.loadTestsFromTestCase(BuildTest)
    from tinycss.tests.main import find_tests
    ans.addTests(find_tests())
    return ans


def test():
    from calibre.utils.run_tests import run_cli
    run_cli(find_tests())


if __name__ == '__main__':
    test()
