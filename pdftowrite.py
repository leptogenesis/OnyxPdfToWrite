#!/usr/bin/python3
import pypdf 
import zlib
import gzip
import argparse,sys
import os

#this is the width and height defined in Write for A4 paper.
#there are the number of pixels in an A4 paper for 150dpi
paperheight=1755;
paperwidth=1240;

def pagesize(name):
   """this function returns the page sizes given in Write. adding an l at the end, converts it to landscape. If no know size is given
      it defaults to A4"""
   match name:
      case "A4":
         return [1240,1755]
      case "A4l":
         return [1755,1240]
      case "Letter":
         return [1275,1650]
      case "Letterl":
         return [1650,1275]
      case "Screen":
         return [810, 1170]
      case "Screenl":
         return [1170,810]
      case _:
         return pagesize("A4")

documenthead="""<svg id="write-document" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
<rect id="write-doc-background" width="100%" height="100%" fill="#808080"/>
"""

def documenttail(n,width,height): 

   str="""
<defs id="write-defs">
<g id="write-pages">"""
   for i in range(1,n):
     str += f"""<use href="#page_{i:>03}" width="{width}" height="{height}"/>"""
   str += """
</g>

<script type="text/writeconfig">
  <int name="docFormatVersion" value="2" />
  <int name="pageNum" value="7" />
  <float name="xOffset" value="-10.5621805" />
  <float name="yOffset" value="706.959106" />
</script>

<style type="text/css"><![CDATA[
  #write-document, #write-doc-background { width: 1260px;  height: 14210px; }
]]></style>
</defs>
</svg>"""
   return str


def pagehead(width,height):
   return f"""<svg class="write-page" color-interpolation="linearRGB" x="0" y="0" width="{width}px" height="{height}px" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <g class="write-content write-v3" xruling="0" yruling="0" marginLeft="0" papercolor="#FFFFFF" rulecolor="#9F0000FF">
    <g class="ruleline write-std-ruling write-scale-down" fill="none" stroke="#0000FF" stroke-opacity="0.624" stroke-width="1" shape-rendering="crispEdges" vector-effect="non-scaling-stroke">
      <rect class="pagerect" fill="#FFFFFF" stroke="none" x="0" y="0" width="1240" height="1755" />
    </g>"""

pagetail="""</g></svg>""";


def smoothen(points):
   """I will define the "smoothen" function here. It will return a smooth bezier curve for the given points.
   the strategy will be:
   i. devide the points into groups such that if one draws lines between successive points, the total length of the line will be 4px(?) and the distance between be start and the end will be 4px(?)"""
def resample(points,N):
   """this function will resample the points. the points recorded by neoreader makes zig zag, hence there are too many points. this will take the average of N consecutive points and replace them by their average."""

def points_to_svgd(points,scale):
   """this function takes the array of points and command and converts them to a d comman to be used in the svg tag path. It also multiplies all coordinates
   by scale. the commands should be upper case, since the coordinates returned from the pdf are absolute coordinates."""
   dstr=" ".join([val[0].upper()+str(val[1]*scale)+" "+str(val[2]*scale) for val in points])
   return dstr

def v_reflect_points(points,height):
   newdata = [[val[0],val[1],height-val[2]] for val in points]
   return newdata

def str_to_points(string):
  """this will take a decoded stream.it will convert the decoded stream into and array of triplets. the first will be the svg command (like M,m,L, l, etc), the remaining two will be 
  the coordinates of the point. later on these points will be converted to an svg command"""
  #this is the split lines
  lines = string.splitlines()
  #here I initialize the aray that will contain the triplets
  points=[]
  #now loop over each line and add the points as they are discovered
  for line in lines:
     #each line can have various formats. possible options are:
     # number w: this appears in ball point pen, it gives the width of the stroke
     # number w number number m number number l S: this appears in Pen and Brush pen.
     # number number l: this appears in ball point
     # number number number RG: this probably specifies the color of the stroke, I can deal with it later
     # S: this appear at the end of ball point pen
     #my strategy will be to look at the last string. the cases I am interested in this function are S, l, m
     # if the line is just "S" with no number, then skip the line
     if len(line)==1:
        continue
     match line[-1]:
        case "S":
           _,_,x1,y1,c1,x2,y2,c2,_=line.split(" ")
           #it might be possible that c1=m, and x1 and y1 are the same as the x2 and y2 from the previous line. in this case, only add x2 and y2
           if len(points)>1:
              if points[-1][1] == float(x1) or points[-1][2] == float(y1):
                 points.extend([[c2,float(x2),float(y2)]])
              else:
                 points.extend([[c1,float(x1),float(y1)],[c2,float(x2),float(y2)]])
           else:
              points.extend([[c1,float(x1),float(y1)],[c2,float(x2),float(y2)]])
        case "l"|"m":
           x1,y1,c1 = line.split(" ")
           points.extend([[c1,float(x1),float(y1)]])
  return points

def get_color_from_annot_object(object):
   """the argument is the annotation object from the pdf reader. It contains info for the color.
   it will return the rbg string that can be used in svg stroke attribute"""
   color =object["/C"]
   svgcolor=f"rgb({color[0]*255},{color[1]*255},{color[2]*255})"
   return svgcolor

def get_alpha_from_annot_object(object):
   """the argument is the annotation object from the pdf reader. It contains info for the color.
   it will return the rbg string that can be used in svg stroke attribute"""
   colora =object["/CA"]
   return colora

def ink_to_svg(annot,scale,height):
   """this function will receive an annotation object whose subtype is "/Ink" or "Stamp". It will return the complete path tag
   the second argument is by how much the corrdinates should be scaled.
   the third argument is the height of the page. for some reason the points are vertically flipped."""
   dcommand=points_to_svgd(v_reflect_points(str_to_points(annot.get_object()["/AP"]["/N"].get_data().decode()),height),scale)
   svgcolor=get_color_from_annot_object(annot)
   svgcolora=get_alpha_from_annot_object(annot)
   #this is the width of the stroke
   svgwidth=annot["/BS"]["/W"]
   svg_string=f"<path d=\""+dcommand+f"\" style=\"stroke:{svgcolor}; stroke-width:{svgwidth};fill:none; stroke-opacity:{svgcolora}; stroke-linejoin:round; stroke-linecap:round\"/>\n"
   return svg_string
 
def text_to_svg(annot,scale,height):
   """this function will receive an annotation whose subtype is "/FreeText". IT will return the complete <text> tag with style,scale
   the second argument is by how much the coordinates should be scaled"""
   content=annot["/RC"]
   #I will extract the style from span to be used in <text>tag
   style=content.split("style=\"")[1].split("\"")[0]
   #now I need to find the transformation matrix that will position the text in the correct position
   #I will use the coordinates of the BBox as the position of the text
   bbox = annot["/AP"]["/N"]["/BBox"]
   x,y,*_ = bbox
   text = annot["/Contents"]
   #for some reason, the scale of the font needs to be further corrected to get results similar to NeoReaders (it is worse in the pdf)
   extrascale=0.5
   svg_string=f"<text transform=\"matrix({extrascale*scale} 0 0 {extrascale*scale} 0 0)\" style=\"{style}\" x=\"{round(x*scale)}\" y=\"{round((height-y)*scale)}\">{text}</text>"
   return svg_string

def polygon_to_svg(annot,scale,height):
   """this function will receive an annotation whose subtype is a polygon. The "/Vertices" is a list of numbers specifying the x and y coordinates of the 
      vertices of the polygon"""
   vertices = annot["/Vertices"]
   iterator = iter(vertices)
   points = ""
   for vert in iterator:
      x,y = [vert,next(iterator)]
      points += f"{x*scale},{(height-y)*scale} "
   svgcolor=get_color_from_annot_object(annot)
   svgcolora=get_alpha_from_annot_object(annot)
   #this is the width of the stroke
   svgwidth=annot["/BS"]["/W"]
   svg_string=f"<polygon points=\"{points}\" style=\"fill:none;stroke:{svgcolor};stroke-opacity:{svgcolora};stroke-width:{svgwidth}\" />"
   return svg_string
   
def circle_to_svg(annot,scale,height):
   """this function will receive an annotation whose subtype is a circle. 
      in the pdf, the "circle" is given as a collection of cubic bezier curves."""
   points = annot["/AP"]["/N"].get_data().decode().splitlines()
   iterator = iter(points)
   dstr="M"
   #the first line is not something I want. I am skipping it
   next(iterator)
   #the second line is the moveto point:
   moveto = next(iterator)
   *_,x,y,_ = moveto.split(" ")
   #moveto seems to be relative to the rectangle. Hence I need to get the coordinates of the rectangle also
   X,Y,*_ = annot["/Rect"]
   dstr += f"{x} {y}" 
   #the rest of the lines are bezier points for the cubic bezier
   for bezier in iterator:
      #the last line has a character s only. This conditional skips it
      if len(bezier) > 3:
         x1,y1,x2,y2,x3,y3,c = bezier.split(" ")
         dstr += f"C {float(x1)} {float(y1)}, {float(x2)} {float(y2)}, {float(x3)} {float(y3)}"
   svgcolor=get_color_from_annot_object(annot)
   svgcolora=get_alpha_from_annot_object(annot)
   #this is the width of the stroke
   svgwidth=annot["/BS"]["/W"]
   svg_string=f"<path transform=\"matrix({scale} 0 0 {-scale} {X*scale} {(height-Y)*scale})\" d=\"{dstr}\" style=\"fill:none;stroke:{svgcolor};stroke-opacity:{svgcolora};stroke-width:{svgwidth}\" />"
   return svg_string
   
   
def pdftowrite(pdfname,outfilename,paperwidth,paperheight):
   """this function does the conversion from pdf to write. Its arguments are the path to the pdf, the name of the output file,
   the width and height of the Write page. It converts the pdf to write document and saves it into outfilename"""
   reader = pypdf.PdfReader(pdfname)
   svg_string=documenthead

   for page in reader.pages:
      svg_string += pagehead(paperwidth,paperheight)
      if not "/Annots" in page:
         print(f"there are no annotations in  page {page.page_number+1}")
         svg_string += pagetail
         continue
      annots=page["/Annots"]
      *_,width,height=page["/MediaBox"]
      scale=min(paperwidth/width,paperheight/height)
      #svg_string+=f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">'
      iterno = int(0)
      for annot in annots:
         #I can check the /SubType of annot. if it is "/Ink", that is will be converted to a path, if it is "/FreeText" it will be the text
         iterno =iterno+1
         print(f"Page {page.page_number+1}/{len(reader.pages)} Completion: {round(iterno/len(annots)*100)}%",end='\r',flush=True)
         match annot["/Subtype"]:
            case "/Ink"|"/Stamp":
               svg_string += ink_to_svg(annot,scale,height)
            case "/FreeText":
               svg_string += text_to_svg(annot,scale,height)
            case "/Polygon":
               svg_string += polygon_to_svg(annot,scale,height)
            case "/Circle":
               svg_string += circle_to_svg(annot,scale,height)
      svg_string += pagetail
      print("")

   svg_string += documenttail(len(reader.pages),paperwidth,paperheight)
   with gzip.open(outfilename,"wt") as f:
      f.write(svg_string)
      f.close()


if __name__=="__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument("inputfile")
   parser.add_argument("outputfile",default="output.svgz")
   parser.add_argument("-s","--size",choices=["A4","A4l","Letter","Letterl","Screen","Screenl","Auto","Custom"],default="A4")
   parser.add_argument("-pw","--pagewidth")
   parser.add_argument("-ph","--pageheight")
   parser.add_argument("-f","--force",action='store_true')
   arguments = vars(parser.parse_args())
   paperwidth, paperheight = [None, None]
   force=arguments["force"]
   outfile=arguments["outputfile"]
   infile=arguments["inputfile"]
   if not os.path.exists(infile):
      sys.exit(f"file {infile} does not exist")
   if os.path.exists(outfile) and not force:
      sys.exit(f"file {outfile} exits. please choose another name or use the -f (--force) option to overwrite the existing file")
   #for custom or Auto size option, I need to find the size of the pdf file.
   reader = pypdf.PdfReader(infile)
   *_, PW,PH = reader.pages[0]["/MediaBox"]
   match arguments["size"]:
      case "A4"|"A4l"|"Letter"|"Letterl"|"Screen"|"Screenl":
         paperwidth,paperheight = pagesize(arguments["size"])
      case "Auto":
         paperwidth=PW
         paperheight=PH
      case "Custom":
         if "width" in arguments or "height" in arguments:
            if "width" in arguments:
               paperwidth=arguments["width"]
            if "height" in arguments:
               paperheight=arguments["height"]
            if paperwidth is None:
               paperwidth= PW*paperheight/PH
            if paperheight is None:
               paperheight = PH*paperwidth/PW
         else:
            sys.exit("You have to specify at least the custom width or cursom height")
      case "_":
         paperwidth,paperheight=pagesize("A4")
   if paperwidth is None or paperheight is None:
      sys.exit("Could not deterime width/hwight of page")
   pdftowrite(arguments["inputfile"],arguments["outputfile"],paperwidth,paperheight)
