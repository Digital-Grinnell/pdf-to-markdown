# From https://github.com/jorisschellekens/borb-examples#32-extracting-text-from-a-pdf
# And https://github.com/jorisschellekens/borb

import re
import unidecode

import typing
from borb.pdf.document import Document
from borb.pdf.pdf import PDF
from borb.toolkit.text.font_name_filter import FontNameFilter
from borb.toolkit.text.simple_text_extraction import SimpleTextExtraction
from borb.toolkit.text.font_extraction import FontExtraction

# extract all fonts... requires debugger to interrogate
def extract_fonts():
    doc: typing.Optional[Document] = None
    l: FontExtraction = FontExtraction()
    with open("evans.pdf", "rb") as pdf_file_handle:
        doc = PDF.loads(pdf_file_handle, [l])
    assert doc is not None
    return  # set a breakpoint here and inspect "l" in order to see all the fonts per page

# extract all paragraph text, assuming it is has a base font of XXCKAM+MinionPro-Regular
def extract_paragraph_text( ):
    doc: typing.Optional[Document] = None
    l0: FontNameFilter = FontNameFilter("XXCKAM+MinionPro-Regular")
    l1: SimpleTextExtraction = SimpleTextExtraction()
    l0.add_listener(l1)
    with open("evans.pdf", "rb") as pdf_file_handle:
        doc = PDF.loads(pdf_file_handle, [l0])
    assert doc is not None
    page_count = l1._current_page + 1

    paragraph = ""
    paragraphs = []

    for page in range(page_count):
        p = l1.get_text_for_page(page)
        lines = p.split("\n")

        for raw_line in lines:
            line = unidecode.unidecode(raw_line)
            if re.match(r"^\d+$", line):     # page number, skip it
                continue
            if (line.endswith('.') and (len(line) < 50)):       # end of the paragraph, save it
                paragraph += line + " "
                paragraphs.append(paragraph)
                paragraph = ""
            elif line.endswith('-'):       # remove dash and append to paragraph
                paragraph += line.rstrip('-')
            else:
                paragraph += line + " "

    for para in paragraphs:
        print(para + "\n")

        # print(l1.get_text_for_page(page))

# extract all caption text, assuming it is has a base font of XXXCKAM+KannadaMN-SC700
def extract_caption_text( ):
    doc: typing.Optional[Document] = None
    l0: FontNameFilter = FontNameFilter("XXCKAM+KannadaMN-SC700")
    l1: SimpleTextExtraction = SimpleTextExtraction()
    l0.add_listener(l1)
    with open("evans.pdf", "rb") as pdf_file_handle:
        doc = PDF.loads(pdf_file_handle, [l0])
    assert doc is not None
    page_count = l1._current_page + 1
    print("Captions are:\n")
    for page in range(page_count):
      print(l1.get_text_for_page(page))

# main
def main():
    # extract_fonts( )
    # extract_caption_text( )
    extract_paragraph_text( )


if __name__ == "__main__":
    main()
