import os
import PyPDF4 as pypdf
import sys
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog

# starts tkinter and hides root
root = tk.Tk()
root.withdraw()

# file selection dialogue
OLD_PDF_FILE_PATH = filedialog.askopenfilename(filetypes = [("Portable Document Format", ".pdf")])

# handles instances of a closed file selection dialogue
if not OLD_PDF_FILE_PATH:
    sys.exit(0)

# opens the old pdf to be edited
# also creates a new pdf instance to which these edits are written
with open(OLD_PDF_FILE_PATH, "rb") as old_pdf:
    old_file = pypdf.PdfFileReader(old_pdf)
    new_file = pypdf.PdfFileWriter()

    # the number of pages in the old file
    amount_of_pages_in_file = old_file.getNumPages()

    # amount of sheets in a signature
    AMOUNT_OF_PAGES_TO_TRIM_FRONT = simpledialog.askinteger(title = "Amount of pages to trim", prompt = f"How many pages should be trimmed from the front? (1-{amount_of_pages_in_file})", minvalue = 1, maxvalue = amount_of_pages_in_file, initialvalue = 1)

    # handles users cancelling dialogue
    if AMOUNT_OF_PAGES_TO_TRIM_FRONT is None:
        sys.exit(0)

    # handles input errors for the signature sheet size dialogue
    while AMOUNT_OF_PAGES_TO_TRIM_FRONT < 1 or AMOUNT_OF_PAGES_TO_TRIM_FRONT > amount_of_pages_in_file:
        messagebox.showwarning("Error", f"Error: invalid amount of pages.\nPlease enter an integer no smaller than 1 and no bigger than {amount_of_pages_in_file}.")
        AMOUNT_OF_PAGES_TO_TRIM_FRONT = simpledialog.askinteger(title = "Amount of pages to trim", prompt = f"How many pages should be trimmed from the front? [1,{amount_of_pages_in_file}]", minvalue = 1, maxvalue = amount_of_pages_in_file, initialvalue = 1)

    # copies all pages but the first one from the old to the new pdf
    for page_num in range(amount_of_pages_in_file):
        if page_num >= AMOUNT_OF_PAGES_TO_TRIM_FRONT:
            page = old_file.getPage(page_num)
            new_file.addPage(page)

    # template for the default filename
    new_file_name = f"{os.path.splitext(os.path.basename(OLD_PDF_FILE_PATH))[0].replace(' ', '_')}_T{AMOUNT_OF_PAGES_TO_TRIM_FRONT}.pdf"

    # gets the file path to which to save the generated pdf
    NEW_PDF_FILE_PATH = filedialog.asksaveasfilename(defaultextension = [(".pdf")], filetypes = [("Portable Document Format", ".pdf")], initialfile = new_file_name)

    # handles instances of a closed location selection dialogue
    if not NEW_PDF_FILE_PATH:
        sys.exit(0)

    # writes the edited pdf to the disk
    with open(NEW_PDF_FILE_PATH, "wb") as write_file:
        new_file.write(write_file)
