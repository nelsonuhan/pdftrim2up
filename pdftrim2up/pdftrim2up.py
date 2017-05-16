import os
import argparse
from PyPDF2 import PdfFileReader, PdfFileWriter


def main():
    '''
    Trim and 2-up PDF file
    '''
    parser = argparse.ArgumentParser(
        description="Trim the margins of a PDF, place them 2-up"
    )
    parser.add_argument("input", metavar="FILE",
                        help="PDF file to trim and 2-up.")
    parser.add_argument(
        "--odd",
        metavar=("ORIGINAL_WIDTH", "ORIGINAL_HEIGHT",
                 "LEFT", "WIDTH", "TOP", "HEIGHT"),
        nargs=6,
        required=True,
        type=int,
        help="Values from Preview.app"
    )
    parser.add_argument(
        "--even",
        metavar=("ORIGINAL_WIDTH", "ORIGINAL_HEIGHT",
                 "LEFT", "WIDTH", "TOP", "HEIGHT"),
        nargs=6,
        required=True,
        type=int,
        help="Values from Preview.app"
    )
    args = parser.parse_args()

    IN = args.input
    ODD_ORIGINAL_WIDTH = args.odd[0]
    ODD_ORIGINAL_HEIGHT = args.odd[1]
    ODD_LEFT = args.odd[2]
    ODD_WIDTH = args.odd[3]
    ODD_TOP = args.odd[4]
    ODD_HEIGHT = args.odd[5]
    EVEN_ORIGINAL_WIDTH = args.even[0]
    EVEN_ORIGINAL_HEIGHT = args.even[1]
    EVEN_LEFT = args.even[2]
    EVEN_WIDTH = args.even[3]
    EVEN_TOP = args.even[4]
    EVEN_HEIGHT = args.even[5]

    # Calculate other constants
    ODD_BOTTOM = ODD_ORIGINAL_HEIGHT - (ODD_TOP + ODD_HEIGHT)
    EVEN_BOTTOM = EVEN_ORIGINAL_HEIGHT - (EVEN_TOP + EVEN_HEIGHT)

    # Regular letter paper dimensions
    OUT_WIDTH = 11.5 * 72 / 2
    OUT_HEIGHT = 8.5 * 72

    # Open file
    in_stream = open(IN, 'rb')
    in_pdf = PdfFileReader(in_stream, strict=False)
    trim_pdf = PdfFileWriter()

    # Trim pages
    print("Trimming ", end="", flush=True)
    for i in range(in_pdf.getNumPages()):
        print(".", end="", flush=True)
        in_page = in_pdf.getPage(i)

        # Odd pages
        if i % 2 == 0:
            trim_page = trim_pdf.insertBlankPage(width=ODD_WIDTH,
                                                 height=ODD_HEIGHT,
                                                 index=trim_pdf.getNumPages())
            trim_page.mergeTranslatedPage(in_page, tx=-ODD_LEFT,
                                          ty=-ODD_BOTTOM)

        # Even pages
        else:
            trim_page = trim_pdf.insertBlankPage(width=EVEN_WIDTH,
                                                 height=EVEN_HEIGHT,
                                                 index=trim_pdf.getNumPages())
            trim_page.mergeTranslatedPage(in_page, tx=-EVEN_LEFT,
                                          ty=-EVEN_BOTTOM)

        trim_page.cropBox = trim_page.mediaBox
        trim_page.trimBox = trim_page.mediaBox

    # Combine two pages into 1
    out_pdf = PdfFileWriter()

    def scale_page(page, side):
        '''
        Get scaling factors
        '''
        width = float(page.mediaBox.upperRight[0])
        height = float(page.mediaBox.upperRight[1])
        scale = min(OUT_WIDTH / width, OUT_HEIGHT / height) * 0.95
        scaled_width = width * scale
        scaled_height = height * scale
        tx = (OUT_WIDTH - scaled_width) / 2
        ty = (OUT_HEIGHT - scaled_height) / 2

        if side == 'right':
            tx += OUT_WIDTH

        return scale, tx, ty

    # First page
    print("\nCombining.", end="", flush=True)
    rhs = trim_pdf.getPage(0)

    page = out_pdf.insertBlankPage(width=OUT_WIDTH * 2, height=OUT_HEIGHT,
                                   index=out_pdf.getNumPages())
    page.cropBox = page.mediaBox
    page.trimBox = page.mediaBox

    scale, tx, ty = scale_page(rhs, side='right')
    page.mergeScaledTranslatedPage(rhs, scale=scale, tx=tx, ty=ty)

    # Second page onwards
    for i in range(1, trim_pdf.getNumPages(), 2):
        print("..", end="", flush=True)

        page = out_pdf.insertBlankPage(width=OUT_WIDTH * 2, height=OUT_HEIGHT,
                                       index=out_pdf.getNumPages())
        page.cropBox = page.mediaBox
        page.trimBox = page.mediaBox

        lhs = trim_pdf.getPage(i)
        scale, tx, ty = scale_page(lhs, side='left')
        page.mergeScaledTranslatedPage(lhs, scale=scale, tx=tx, ty=ty)

        try:
            rhs = trim_pdf.getPage(i + 1)
        except IndexError:
            pass
        else:
            scale, tx, ty = scale_page(rhs, side='right')
            page.mergeScaledTranslatedPage(rhs, scale=scale, tx=tx, ty=ty)

    # Create output filename
    in_abspath = os.path.abspath(IN)
    in_basename, in_ext = os.path.splitext(in_abspath)
    out_filename = in_basename + '_trim2up' + in_ext

    # Output file
    out_stream = open(out_filename, 'wb')
    out_pdf.write(out_stream)

    # Close file streams
    in_stream.close()
    out_stream.close()
