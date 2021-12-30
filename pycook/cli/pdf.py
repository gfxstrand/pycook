#! /usr/bin/env python3
#
# Copyright © 2020 Jason Ekstrand
#
# PyCook is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# PyCook is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# PyCook.  If not, see <https://www.gnu.org/licenses/>.

import os
import shutil
import subprocess
import tempfile

from ..cookbook import Cookbook

def to_avery5389(infile, front_out, back_out=None):
    from PyPDF2 import PdfFileReader, PdfFileWriter
    from PyPDF2.pdf import PageObject

    inpdf = PdfFileReader(infile)
    front_out_pdf = PdfFileWriter()
    if back_out:
        back_out_pdf = PdfFileWriter()
    else:
        back_out_pdf = front_out_pdf

    num_in_pages = inpdf.getNumPages()
    num_out_sheets = (num_in_pages + 3) // 4
    for i in range(num_out_sheets):
        front = PageObject.createBlankPage(None, 612, 792)
        back = PageObject.createBlankPage(None, 612, 792)

        front.mergeTranslatedPage(inpdf.getPage(i * 4 + 0), 90, 396)
        if i * 4 + 2 < num_in_pages:
            front.mergeTranslatedPage(inpdf.getPage(i * 4 + 2), 90, 108)
        if i * 4 + 1 < num_in_pages:
            back.mergeTranslatedPage(inpdf.getPage(i * 4 + 1), 90, 396)
        if i * 4 + 3 < num_in_pages:
            back.mergeTranslatedPage(inpdf.getPage(i * 4 + 3), 90, 108)

        front_out_pdf.addPage(front)
        back_out_pdf.addPage(back)

    with open(front_out, 'wb') as f:
        front_out_pdf.write(f)
    if back_out:
        with open(back_out, 'wb') as f:
            back_out_pdf.write(f)

def main(args):
    if args.style == 'avery5389':
        style = '4x6cards'
    else:
        style = args.style

    tmpdir = tempfile.mkdtemp(prefix='cookbook')
    try:
        background = None
        if args.background:
            background = os.path.basename(args.background)
            shutil.copyfile(args.background, os.path.join(tmpdir, background))

        c = Cookbook.load(args.input)
        with open(os.path.join(tmpdir, 'cookbook.tex'), 'w') as f:
            f.write(c.to_latex(style=style, background=background))

        subprocess.run([
            'latexmk',
            '-cd',
            '-pdf',
            os.path.join(tmpdir, 'cookbook.tex')
        ])

        if args.style == 'cookbook' or args.style == '4x6cards':
            shutil.copyfile(os.path.join(tmpdir, 'cookbook.pdf'), args.output)
        elif args.style == 'avery5389':
            if args.separate:
                base, ext = os.path.splitext(args.output)
                to_avery5389(os.path.join(tmpdir, 'cookbook.pdf'),
                             base + '-front' + ext, base + '-back' + ext)
            else:
                to_avery5389(os.path.join(tmpdir, 'cookbook.pdf'),
                             args.output)
        else:
            assert False

    except:
        shutil.rmtree(tmpdir)
        raise

    shutil.rmtree(tmpdir)

def setup_subparser(subparser):
    subparser.add_argument('-s', '--style', type=str, default='cookbook',
                           choices=['cookbook', '4x6cards', 'avery5389'],
                           help='Style of PDF to generate')
    subparser.add_argument('-S', '--separate', action='store_const',
                           const=True, default=False,
                           help='Produce separate front and back PDFs')
    subparser.add_argument('-b', '--background', help='Background image')
    subparser.add_argument('input', help='Name of input file', )
    subparser.add_argument('output', help='Name of output file')
    subparser.set_defaults(func=main)
