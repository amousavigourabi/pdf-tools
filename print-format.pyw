import math
import os
import PyPDF4 as pypdf
import sys
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog

# starts tkinter and hides root
root = tk.Tk()
root.withdraw()

# amount of sheets in a signature
SIGNATURE_SHEET_SIZE = simpledialog.askinteger(title = "Signature size", prompt = "How many sheets does a signature consist of? [1,16]", minvalue = 1, maxvalue = 16, initialvalue = 4)

# handles users cancelling dialogue
if SIGNATURE_SHEET_SIZE is None:
    sys.exit(0)

# handles input errors for the signature sheet size dialogue
while SIGNATURE_SHEET_SIZE < 1 or SIGNATURE_SHEET_SIZE > 16:
    messagebox.showwarning("Error", "Error: invalid signature sheet size.\nPlease enter an integer no smaller than 1 and no bigger than 16.")
    SIGNATURE_SHEET_SIZE = simpledialog.askinteger(title = "Signature size", prompt = "How many sheets does a signature consist of? [1,16]", minvalue = 1, maxvalue = 16, initialvalue = 4)

# amount of pages in a signature
SIGNATURE_PAGE_SIZE = 4 * SIGNATURE_SHEET_SIZE

# the variable with which pages are shifted
# although normally this variable is 0
# when the first x pages are redundant it is equal to x
PAGE_SHIFT = simpledialog.askinteger(title = "Content formatting", prompt = "How many of the first pages are redundant? [0,16]", minvalue = 0, maxvalue = 16, initialvalue = 0)

# handles users cancelling dialogue
if PAGE_SHIFT is None:
    sys.exit(0)

# handles input errors for the first page redundancy dialogue
while PAGE_SHIFT < 0 or PAGE_SHIFT > 16:
    messagebox.showwarning("Error", "Error: invalid amount of pages to trim\nPlease enter an integer no smaller than 0 and no bigger than 16.")
    PAGE_SHIFT = simpledialog.askinteger(title = "Content formatting", prompt = "How many of the first pages are redundant? [0,16]", minvalue = 0, maxvalue = 16, initialvalue = 0)

# creates the new pdf
new_pdf = pypdf.PdfFileWriter()

# file selection dialogue
OLD_PDF_FILE_PATH = filedialog.askopenfilename(filetypes = [("Portable Document Format", ".pdf")])

# handles instances of a closed file selection dialogue
if not OLD_PDF_FILE_PATH:
    sys.exit(0)

# opens the selected pdf file
with open(OLD_PDF_FILE_PATH, "rb") as pdf:
    original_pdf = pypdf.PdfFileReader(pdf)

    # retrieves the number of pages of the target pdf
    number_of_pages = original_pdf.getNumPages()

    # handles redundant first pages
    if PAGE_SHIFT > 0:
        number_of_pages -= 1

    # number of pages rounded up to a fourfold number
    if number_of_pages % 4 != 0:
        ceil_number_of_pages = 4 * math.ceil(number_of_pages / 4)
    else:
        ceil_number_of_pages = number_of_pages

    new_file_name = f"{os.path.splitext(os.path.basename(OLD_PDF_FILE_PATH))[0].replace(' ', '_')}_T{PAGE_SHIFT}_S{SIGNATURE_SHEET_SIZE}_P{ceil_number_of_pages}_printready"

    # orders the pages
    # iterates over every signature
    for i in range(math.ceil(number_of_pages / SIGNATURE_PAGE_SIZE)):
        # the page range to work with in this signature
        signature_first_page = SIGNATURE_PAGE_SIZE * i + PAGE_SHIFT
        if SIGNATURE_PAGE_SIZE * (i + 1) > ceil_number_of_pages:
            signature_last_page = ceil_number_of_pages + PAGE_SHIFT - 1
        else:
            signature_last_page = SIGNATURE_PAGE_SIZE * (i + 1) + PAGE_SHIFT - 1

        # iterates per sheet in the signature
        for j in range(int((signature_last_page - signature_first_page + 1) / 4)):
            # adds the appropriate page to the document
            # when the final pages are blank to fill a signature a blank page is added
            if signature_last_page < number_of_pages:
                new_pdf.addPage(original_pdf.getPage(signature_last_page))
            # iff the new pdf is still empty, addBlankPage is in need of explicit width and height params
            # for this we take the width and height of the first page
            elif (i == 0) and (j == 0):
                new_pdf.addBlankPage(width = original_pdf.getPage(0).mediaBox[2], height = original_pdf.getPage(0).mediaBox[3])
            else:
                new_pdf.addBlankPage()

            if signature_first_page < number_of_pages:
                new_pdf.addPage(original_pdf.getPage(signature_first_page))
            else:
                new_pdf.addBlankPage()

            # increases and decreases the page numbers by one
            # working its way to the middle from the edges
            signature_first_page += 1
            signature_last_page -= 1

            if signature_first_page < number_of_pages:
                new_pdf.addPage(original_pdf.getPage(signature_first_page))
            else:
                new_pdf.addBlankPage()

            if signature_last_page < number_of_pages:
                new_pdf.addPage(original_pdf.getPage(signature_last_page))
            else:
                new_pdf.addBlankPage()

            # increasing and decreasing the counters to work its way to the middle
            # as is the case above
            signature_first_page += 1
            signature_last_page -= 1

    # gets the file path to which to save the generated pdf
    NEW_PDF_FILE_PATH = filedialog.asksaveasfilename(defaultextension = [(".pdf")], filetypes = [("Portable Document Format", ".pdf")], initialfile = new_file_name)

    # handles instances of a closed location selection dialogue
    if not NEW_PDF_FILE_PATH:
        sys.exit(0)

    # saves the generated file at the selected filepath
    with open(NEW_PDF_FILE_PATH, "wb") as write_file:
        new_pdf.write(write_file)
