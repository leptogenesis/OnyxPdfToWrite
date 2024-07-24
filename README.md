# OnyxPdfToWrite
<h1>pdftowrite</h1>
<em>pdftowrite.py</em> python script converts a pdf created by Onyx Boox to an svgz file for <a href="https://www.styluslabs.com"> Stylus Labs Write </a>

I tested in on PDF's created/annotated on Onyx Boox 3 running Android 12.

It successfully converts text, shapes and various brushes. It fails to convert (for some reason that I could not find yet) the Ink created by Pencil.

<h2> Usage: </h2>
usage: pdftowrite.py [-h] [-s {A4,A4l,Letter,Letterl,Screen,Screenl,Auto,Custom}] [-pw PAGEWIDTH] [-ph PAGEHEIGHT] [-f] inputfile outputfile<br>
<br>
positional arguments:<br>
&nbsp;&nbsp;inputfile<br>
&nbsp;&nbsp;outputfile<br>

options:<br>
&nbsp;&nbsp;-h, --help            show this help message and exit<br>
&nbsp;&nbsp;-s {A4,A4l,Letter,Letterl,Screen,Screenl,Auto,Custom}, --size {A4,A4l,Letter,Letterl,Screen,Screenl,Auto,Custom}<br>
&nbsp;&nbsp;-pw PAGEWIDTH, --pagewidth PAGEWIDTH<br>
&nbsp;&nbsp;-ph PAGEHEIGHT, --pageheight PAGEHEIGHT<br>
&nbsp;&nbsp;-f, --force <br>

where the inputfile is the pdf file to be converted<br>
the outputfile is the name the svgz file will have. If file exists, it will not be overwritten unless "-f/--force" is passed as an option<br>

"-s/--size" chooses the size of the page in the Write file. Write comes with A4, Letter and Screen sizes predefined. The definitions used in the script coincide with the sizes define in Write.<br>

using -s Custom, one can define the pagewidth and pageheight.<br>

If Auto is chose, size given in the pdf will be used<br>

size defaults to A4.<br>
#
<h1>PdftoTex</h1>

<em>pdftotex.py</em> takes the pdf file created by boox and tries to convert it to a latex file that can be compiled by pdflatex. The Ink are converted into tikzpictures. You should run pdflatex twice on the created file to get everything in their correct position.
