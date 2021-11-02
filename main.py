# From https://github.com/jorisschellekens/borb-examples#32-extracting-text-from-a-pdf
# And https://github.com/jorisschellekens/borb

import re
import unidecode
import os

import typing
from borb.pdf.document import Document
from borb.pdf.pdf import PDF
from borb.toolkit.text.font_name_filter import FontNameFilter
from borb.toolkit.text.simple_text_extraction import SimpleTextExtraction
from borb.toolkit.text.font_extraction import FontExtraction

frontmatter = "---\ntitle: \ndate: \ndraft: false \nauthor: \narticletype: \nazure_header: \nazure_headshot: \nauthorbio: \ndescription: \n---\n"


# process as paragraphs
def process_paragraphs(l1, page_count):
    paragraph = ""
    paragraphs = []

    for page in range(page_count):
        p = l1.get_text_for_page(page)
        lines = p.split("\n")

        for raw_line in lines:
            line = unidecode.unidecode(raw_line)
            if re.match(r"^\d+$", line):  # page number, skip it
                continue
            if (line.endswith('.') and (len(line) < 50)):  # end of the paragraph, save it
                paragraph += line + " "
                paragraphs.append(paragraph)
                paragraph = ""
            elif line.endswith('-'):  # remove dash and append to paragraph
                paragraph += line.rstrip('-')
            else:
                paragraph += line + " "

    # if the last paragraph is not blank, add it to the list
    if len(paragraph) > 0:
        paragraphs.append(paragraph)

    return paragraphs


# extract all fonts
def extract_fonts(pdf):
    doc: typing.Optional[Document] = None
    l: FontExtraction = FontExtraction()
    doc = PDF.loads(pdf, [l])
    assert doc is not None

    # build a list of all BaseFont names (strings) and return it
    font_names = []  # set a breakpoint here and inspect "l" in order to see all the fonts per page
    for page in l._fonts_per_page:
        for font in l._fonts_per_page[page]:
            name = font["BaseFont"]._text
            if name not in font_names:
                font_names.append(name)
                print("Font name {} added to the list.".format(name))
    return font_names


# extract all text that uses the named font...
def extract_paragraph_text(pdf, font):
    doc: typing.Optional[Document] = None
    l0: FontNameFilter = FontNameFilter(font)
    l1: SimpleTextExtraction = SimpleTextExtraction()
    l0.add_listener(l1)
    doc = PDF.loads(pdf, [l0])
    assert doc is not None
    page_count = l1._current_page + 1
    paragraphs = process_paragraphs(l1, page_count)
    # return the paragraphs in order
    return(paragraphs)


def fix_word_case(t):
    fixed = []
    words = t.split(" ")
    for word in words:
        if len(word) > 0:
            if word[0].isupper():
              fixed.append(word.capitalize())
            else:
              fixed.append(word.lower())
    return ' '.join(fixed)



# main
def main():

    # Iterate over the working directory tree subdirectories
    for subdir, dirs, files in os.walk(r'.'):
        for filename in files:
            filepath = subdir + os.sep + filename

            # Looking for .pdf files...
            if filepath.endswith(".pdf"):
                print("Found .pdf file: " + filepath)
                # open the .pdf for processing
                with open(filepath, "rb") as pdf:
                    # open a new .md file to receive translated text
                    (path, filename) = os.path.split(filepath)
                    (name, ext) = filename.split('.')
                    new_file = '{}/{}.{}'.format(path, name, 'md')
                    print("Creating new .md file: " + new_file)
                    with open(new_file, "w") as md:
                      print("{}".format(frontmatter), file=md)
                      font_list = extract_fonts(pdf)
                      for font in font_list:
                          print("\n\n# The following text uses font {}:\n".format(font), file=md)
                          text_array = extract_paragraph_text(pdf, font)
                          for paragraph in text_array:
                            txt = fix_word_case(paragraph)
                            print("{}  \n".format(txt), file=md)


if __name__ == "__main__":
    main()
