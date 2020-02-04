# -*- coding: utf-8 -*-
import sys

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

try:
    from hgext import color

    colorext = color
except ImportError:
    colorext = None
try:
    from mercurial import color
    from mercurial.util import version as mercurial_version
    from diff_highlight import colorui
except ImportError:
    color = None


class TestDiffHighlight(unittest.TestCase):
    @unittest.skipIf(color is None, "mercurial is not supported py3")
    def test_colorui(self):
        try:
            import curses

            curses.setupterm("xterm", 1)
        except ImportError:
            pass

        ui = colorui()
        if mercurial_version() >= b"4.2.0":
            ui.setconfig(b'ui', b'color', b'always')
            color.setup(ui)
            styles = ui._styles
        else:
            colorui.__bases__ = (colorext.colorui,)
            styles = color._styles
        styles[b'diff.inserted_highlight'] = b'green inverse'
        styles[b'diff.deleted_highlight'] = b'red inverse'

        if mercurial_version() >= b"3.7.0":
            ui.pushbuffer(labeled=True)
        else:
            ui.pushbuffer()

        ui.write(b"@@ -10,4 +10,6 @@")
        ui.write(b"\n", b'')
        ui.write(b" ", b'')
        ui.write(b"\n", b'')
        ui.write(b"-print 'nice', 'boat'", label=b'diff.deleted')
        ui.write(b"-print \"bye world\"", label=b'diff.deleted')
        ui.write(b"+print 'hello', 'world'", label=b'diff.inserted')
        ui.write(b"+", label=b'diff.inserted')
        ui.write(b"+", label=b'diff.inserted')
        ui.write(b"+print 'bye world'", label=b'diff.inserted')
        ui.write(b" ", b'')
        ui.write(b"\n", b'')

        if mercurial_version() >= b"4.2.0":
            stop = b"\x1b[0m"

            def start(*colors):
                return b"\x1b[0;" + ";".join(str(c) for c in colors).encode() + b"m"

            def restart(*colors):
                return stop + start(*colors)
        else:
            stop = b"\x1b(B\x1b[m"

            def start(*colors):
                return stop + b"".join(b"\x1b[%dm" % c for c in colors)

            def restart(*colors):
                return stop + start(*colors)

        if mercurial_version() >= b"3.7.0":
            lines = ui.popbuffer().splitlines()
        else:
            lines = ui.popbuffer(True).splitlines()
        self.assertEqual(9, len(lines))
        self.assertEqual(b"@@ -10,4 +10,6 @@", lines[0])
        self.assertEqual(b" ", lines[1])
        self.assertEqual((b"%s-print '%snice%s', '%sboat%s'%s" %
                          (start(31), restart(31, 7), restart(31),
                           restart(31, 7), restart(31), stop)),
                         lines[2])
        self.assertEqual((b"%s+print '%shello%s', '%sworld%s'%s" %
                          (start(32), restart(32, 7), restart(32),
                           restart(32, 7), restart(32), stop)),
                         lines[3])
        self.assertEqual(b"%s+%s" % (start(32), stop), lines[4])
        self.assertEqual(b"%s+%s" % (start(32), stop), lines[5])
        self.assertEqual((b"%s-print %s\"%sbye world%s\"%s" %
                          (start(31), restart(31, 7), restart(31),
                           restart(31, 7), stop)),
                         lines[6])
        self.assertEqual((b"%s+print %s'%sbye world%s'%s" %
                          (start(32), restart(32, 7), restart(32),
                           restart(32, 7), stop)),
                         lines[7])
        self.assertEqual(b" ", lines[8])
