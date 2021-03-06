#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import with_statement, print_function

__license__   = 'GPL v3'
__copyright__ = '2009, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'

import os, re, shutil, zipfile, glob, time, sys, hashlib, json, errno
from zlib import compress
from itertools import chain
is_ci = os.environ.get('CI', '').lower() == 'true'

from setup import Command, basenames, __appname__, download_securely, dump_json
from polyglot.builtins import codepoint_to_chr, itervalues, iteritems, only_unicode_recursive


def get_opts_from_parser(parser):
    def do_opt(opt):
        for x in opt._long_opts:
            yield x
        for x in opt._short_opts:
            yield x
    for o in parser.option_list:
        for x in do_opt(o):
            yield x
    for g in parser.option_groups:
        for o in g.option_list:
            for x in do_opt(o):
                yield x


class Kakasi(Command):  # {{{

    description = 'Compile resources for unihandecode'

    KAKASI_PATH = os.path.join(Command.SRC,  __appname__,
            'ebooks', 'unihandecode', 'pykakasi')

    def run(self, opts):
        self.records = {}
        src = self.j(self.KAKASI_PATH, 'kakasidict.utf8')
        dest = self.j(self.RESOURCES, 'localization',
                'pykakasi','kanwadict2.calibre_msgpack')
        base = os.path.dirname(dest)
        if not os.path.exists(base):
            os.makedirs(base)

        if self.newer(dest, src):
            self.info('\tGenerating Kanwadict')

            for line in open(src, "rb"):
                self.parsekdict(line)
            self.kanwaout(dest)

        src = self.j(self.KAKASI_PATH, 'itaijidict.utf8')
        dest = self.j(self.RESOURCES, 'localization',
                'pykakasi','itaijidict2.calibre_msgpack')

        if self.newer(dest, src):
            self.info('\tGenerating Itaijidict')
            self.mkitaiji(src, dest)

        src = self.j(self.KAKASI_PATH, 'kanadict.utf8')
        dest = self.j(self.RESOURCES, 'localization',
                'pykakasi','kanadict2.calibre_msgpack')

        if self.newer(dest, src):
            self.info('\tGenerating kanadict')
            self.mkkanadict(src, dest)

    def mkitaiji(self, src, dst):
        dic = {}
        for line in open(src, "rb"):
            line = line.decode('utf-8').strip()
            if line.startswith(';;'):  # skip comment
                continue
            if re.match(r"^$",line):
                continue
            pair = re.sub(r'\\u([0-9a-fA-F]{4})', lambda x:codepoint_to_chr(int(x.group(1),16)), line)
            dic[pair[0]] = pair[1]
        from calibre.utils.serialize import msgpack_dumps
        with open(dst, 'wb') as f:
            f.write(msgpack_dumps(dic))

    def mkkanadict(self, src, dst):
        dic = {}
        for line in open(src, "rb"):
            line = line.decode('utf-8').strip()
            if line.startswith(';;'):  # skip comment
                continue
            if re.match(r"^$",line):
                continue
            (alpha, kana) = line.split(' ')
            dic[kana] = alpha
        from calibre.utils.serialize import msgpack_dumps
        with open(dst, 'wb') as f:
            f.write(msgpack_dumps(dic))

    def parsekdict(self, line):
        line = line.decode('utf-8').strip()
        if line.startswith(';;'):  # skip comment
            return
        (yomi, kanji) = line.split(' ')
        if ord(yomi[-1:]) <= ord('z'):
            tail = yomi[-1:]
            yomi = yomi[:-1]
        else:
            tail = ''
        self.updaterec(kanji, yomi, tail)

    def updaterec(self, kanji, yomi, tail):
        key = "%04x"%ord(kanji[0])
        if key in self.records:
            if kanji in self.records[key]:
                rec = self.records[key][kanji]
                rec.append((yomi,tail))
                self.records[key].update({kanji: rec})
            else:
                self.records[key][kanji]=[(yomi, tail)]
        else:
            self.records[key] = {}
            self.records[key][kanji]=[(yomi, tail)]

    def kanwaout(self, out):
        from calibre.utils.serialize import msgpack_dumps
        with open(out, 'wb') as f:
            dic = {}
            for k, v in iteritems(self.records):
                dic[k] = compress(msgpack_dumps(v))
            f.write(msgpack_dumps(dic))

    def clean(self):
        kakasi = self.j(self.RESOURCES, 'localization', 'pykakasi')
        if os.path.exists(kakasi):
            shutil.rmtree(kakasi)
# }}}


class Resources(Command):  # {{{

    description = 'Compile various needed calibre resources'
    sub_commands = ['kakasi', 'mathjax']

    def run(self, opts):
        from calibre.utils.serialize import msgpack_dumps
        scripts = {}
        for x in ['console']:
            for name in basenames[x]:
                if name in ('calibre-complete', 'calibre_postinstall'):
                    continue
                scripts[name] = x

        dest = self.j(self.RESOURCES, 'scripts.calibre_msgpack')
        if self.newer(dest, self.j(self.SRC, 'calibre', 'linux.py')):
            self.info('\tCreating ' + self.b(dest))
            with open(dest, 'wb') as f:
                f.write(msgpack_dumps(scripts))

        recipe_icon_dir = self.a(self.j(self.RESOURCES, '..', 'recipes',
            'icons'))
        dest = os.path.splitext(dest)[0] + '.zip'
        files = glob.glob(self.j(recipe_icon_dir, '*.png'))
        if self.newer(dest, files):
            self.info('\tCreating builtin_recipes.zip')
            with zipfile.ZipFile(dest, 'w', zipfile.ZIP_STORED) as zf:
                for n in sorted(files, key=self.b):
                    with open(n, 'rb') as f:
                        zf.writestr(self.b(n), f.read())

        dest = self.j(self.RESOURCES, 'ebook-convert-complete.calibre_msgpack')
        files = []
        for x in os.walk(self.j(self.SRC, 'calibre')):
            for f in x[-1]:
                if f.endswith('.py'):
                    files.append(self.j(x[0], f))
        if self.newer(dest, files):
            self.info('\tCreating ' + self.b(dest))
            complete = {}
            from calibre.ebooks.conversion.plumber import supported_input_formats
            complete['input_fmts'] = set(supported_input_formats())
            from calibre.customize.ui import available_output_formats
            complete['output'] = set(available_output_formats())
            from calibre.ebooks.conversion.cli import create_option_parser
            from calibre.utils.logging import Log
            log = Log()
            # log.outputs = []
            for inf in supported_input_formats():
                if inf in ('zip', 'rar', 'oebzip'):
                    continue
                for ouf in available_output_formats():
                    of = ouf if ouf == 'oeb' else 'dummy.'+ouf
                    p = create_option_parser(('ec', 'dummy1.'+inf, of, '-h'),
                            log)[0]
                    complete[(inf, ouf)] = [x+' 'for x in
                            get_opts_from_parser(p)]

            with open(dest, 'wb') as f:
                f.write(msgpack_dumps(only_unicode_recursive(complete)))

    def clean(self):
        for x in ('scripts', 'ebook-convert-complete'):
            x = self.j(self.RESOURCES, x+'.pickle')
            if os.path.exists(x):
                os.remove(x)
        from setup.commands import kakasi
        kakasi.clean()
        for x in ('builtin_recipes.xml', 'builtin_recipes.zip',
                'template-functions.json', 'user-manual-translation-stats.json'):
            x = self.j(self.RESOURCES, x)
            if os.path.exists(x):
                os.remove(x)
# }}}
