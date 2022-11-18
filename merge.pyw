import os
import PyPDF4 as pypdf
import sys
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

try:
    # starts tkinter and hides root
    root = tk.Tk()
    root.withdraw()

    # asks whether to append an extra page to uneven pdfs before merging them
    ADD_TO_EVEN = messagebox.askyesnocancel("Length normalization", "Should all pdf files that are appended have an even number of pages?")

    # creates a temporary directory if it does not already exist
    os.makedirs("temp/", exist_ok = True)

    # initializes a list of temporary filepaths to delete after the program ends
    cleanup_paths = []

    # initializes the number of temporary files created
    n = 1

    # handles instances of a closed dialogue
    if ADD_TO_EVEN is None:
        sys.exit(0)

    # file selection dialogue
    PDF_PATH_LIST = filedialog.askopenfilenames(filetypes = [("Portable Document Format", ".pdf")])

    # initializing the counter for the final number of pages
    number_of_pages = 0

    # handles instances of a closed file selection dialogue
    if not PDF_PATH_LIST:
        sys.exit(0)

    # handles instances of a user selecting fewer than 2 files
    while len(PDF_PATH_LIST) < 2:
        messagebox.showwarning("Error", "Error: fewer than 2 files were selected\nPlease select two or more files to merge")
        PDF_PATH_LIST = filedialog.askopenfilenames(filetypes = [("Portable Document Format", ".pdf")])

    # initializes the pdf in which to merge the files
    merge_pdf = pypdf.PdfFileMerger()

    # iterates over the paths of files to merge and appends them to the new pdf
    for pdf_path in PDF_PATH_LIST:
        pdf_to_append = pypdf.PdfFileReader(open(pdf_path, "rb"))
        merge_pdf.append(pdf_to_append, bookmark = os.path.splitext(os.path.basename(pdf_path))[0], import_bookmarks = False)

        # adds the number of pages of the pdf to be appended to the tally of the total number of pages for the filename template
        num_of_pages_to_append = pdf_to_append.getNumPages()
        number_of_pages += num_of_pages_to_append

        # adds a blank page when a file with an uneven amount of pages would be appended and the flag is set
        if ADD_TO_EVEN and num_of_pages_to_append % 2 == 1:
            last_page = pdf_to_append.getPage(num_of_pages_to_append - 1)
            blank_page = pypdf.PdfFileWriter()
            blank_page.addBlankPage(width = last_page.mediaBox.getWidth(), height = last_page.mediaBox.getHeight())

            # the path template of the temporary file to be created
            BLANK_PAGE_PATH = f"temp/tempbd{time.strftime('%Y%m%d')}{n}.pdf"

            # creates the temporary blank page pdf file and adds it to the cleanup list
            with open(BLANK_PAGE_PATH, "wb") as write_file:
                try:
                    blank_page.write(write_file)
                finally:
                    cleanup_paths.append(BLANK_PAGE_PATH)
                    n += 1

            # opens the temporary blank page just created
            opened_blank_page = open(BLANK_PAGE_PATH, "rb")

            # appends the blank page to the end of the file
            blank_page_append = pypdf.PdfFileReader(opened_blank_page)
            merge_pdf.append(blank_page_append)

            # closes the temporary blank page
            opened_blank_page.close()

            # increases the counter for the number of pages in the new file by one
            number_of_pages += 1

    # gets the number of pdf files that have been appended
    number_of_files = len(PDF_PATH_LIST)

    # template string for the default save filename
    new_file_name = f"Z{number_of_files}_P{number_of_pages}_merged"

    # gets the file path to which to save the generated pdf
    NEW_PDF_FILE_PATH = filedialog.asksaveasfilename(defaultextension = [(".pdf")], filetypes = [("Portable Document Format", ".pdf")], initialfile = new_file_name)

    # handles instances of a closed location selection dialogue
    if not NEW_PDF_FILE_PATH:
        sys.exit(0)

    # saves the generated file at the selected filepath
    with open(NEW_PDF_FILE_PATH, "wb") as write_file:
        merge_pdf.write(write_file)

# cleans up the temporary files after the program ends
finally:
    for remove_location in cleanup_paths:
        os.remove(remove_location)
    
    # removes the temp dir iff its empty now
    try:
        os.rmdir("temp/")
    except OSError:
        pass
