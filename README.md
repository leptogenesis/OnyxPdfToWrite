# OnyxPdfToWrite

This python script converts a pdf created by Onyx Boox to an svgz file for <a href="https://www.styluslabs.com"> Stylus Labs Write </a>

I tested in on PDF's created/annotated on Onyx Boox 3 running Android 12.

It successfully converts text, shapes and various brushes. It fails to convert (for some reason that I could not find yet) the Ink created by Pencil.

<h2> Usage: </h2>
usage: pdftowrite.py [-h] [-s {A4,A4l,Letter,Letterl,Screen,Screenl,Auto,Custom}] [-pw PAGEWIDTH] [-ph PAGEHEIGHT] [-f] inputfile outputfile

positional arguments:
  inputfile
  outputfile

options:
  -h, --help            show this help message and exit
  -s {A4,A4l,Letter,Letterl,Screen,Screenl,Auto,Custom}, --size {A4,A4l,Letter,Letterl,Screen,Screenl,Auto,Custom}
  -pw PAGEWIDTH, --pagewidth PAGEWIDTH
  -ph PAGEHEIGHT, --pageheight PAGEHEIGHT
  -f, --force

where the inputfile is the pdf file to be converted
the outputfile is the name the svgz file will have. If file exists, it will not be overwritten unless "-f/--force" is passed as an option

"-s/--size" chooses the size of the page in the Write file. Write comes with A4, Letter and Screen sizes predefined. The definitions used in the script coincide with the sizes define in Write.

using -s Custom, one can define the pagewidth and pageheight.

If Auto is chose, size given in the pdf will be used

size defaults to A4.
