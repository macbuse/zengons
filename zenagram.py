#!$HOME/anaconda/bin/python
# -*- coding: utf-8 -*-
'''
Ripped from template.py 
- makes a "zenagon"
'''

import inkex       # Required
import simplestyle # will be needed here for styles support
import os          # here for alternative debug method only - so not usually required.


__version__ = '0.1'

inkex.localize()



### Your helper functions go here


def cplxs2pts(zs):
    tt = []
    for z in zs:
        tt.extend([z.real,z.imag])
    return tt


def  zen_tris(t = .1,
           depth=10,
           base_triangle=[0,200,200J],
           edges=True):
    
    tris  = [ base_triangle[:] ]
    
    indxs = [0,1,2,0]
    edges = zip(indxs, indxs[1:])
    for k in range(depth):
        tt = tris[-1]
        tris.append([ t*tt[i]  + (1-t)*tt[j] for i,j in edges] )
    
    return tris
        
    
def zengon(t = .1,
           depth=10,
           base_triangle=[0,200,200J],
           edges=True):
    
    pts  = base_triangle[:]
    pts.append(base_triangle[0])
    
    for k in range(depth*3):
        pts.append(t*pts[-2] + (1-t)*pts[-3])
    
    tx,ty = pts[0].real,pts[0].imag
    if not edges:
         pts = pts[3:]
    
    pts = ['%.2f,%.2f'%(z.real,z.imag) for z in pts ]
    return  "M %f %f L %s  "%(tx,ty,' '.join(pts))
      
    


class Myextension(inkex.Effect): # choose a better name
    
    def __init__(self):
        " define how the options are mapped from the inx file "
        inkex.Effect.__init__(self) # initialize the super class
        
        # Two ways to get debug info:
        # OR just use inkex.debug(string) instead...
        try:
            self.tty = open("/dev/tty", 'w')
        except:
            self.tty = open(os.devnull, 'w')  # '/dev/null' for POSIX, 'nul' for Windows.
            # print >>self.tty, "gears-dev " + __version__
            
        # list of parameters defined in the .inx file
        self.OptionParser.add_option("-t", "--num_lines",
                                     action="store", type="int",
                                     dest="depth", default=10,
                                     help="command line help")
        
        self.OptionParser.add_option("-d", "--shrink_ratio",
                                     action="store", type="float",
                                     dest="shrink_ratio", default=0.5,
                                     help="command line help")
        
        
        self.OptionParser.add_option("-x", "--mk_edges",
                                     action="store", type="inkbool", 
                                     dest="mk_edges", default=True,
                                     help="command line help")
        
        self.OptionParser.add_option("-r", "--mk_filled",
                                     action="store", type="inkbool", 
                                     dest="mk_filled", default=False,
                                     help="command line help")


        # here so we can have tabs - but we do not use it directly - else error
        self.OptionParser.add_option("", "--active-tab",
                                     action="store", type="string",
                                     dest="active_tab", default='title', # use a legitmate default
                                     help="Active tab.")
        
 
           
    def calc_unit_factor(self):
        """ return the scale factor for all dimension conversions.
            - The document units are always irrelevant as
              everything in inkscape is expected to be in 90dpi pixel units
        """
        # namedView = self.document.getroot().find(inkex.addNS('namedview', 'sodipodi'))
        # doc_units = self.getUnittouu(str(1.0) + namedView.get(inkex.addNS('document-units', 'inkscape')))
        unit_factor = self.getUnittouu(str(1.0) + self.options.units)
        return unit_factor


### -------------------------------------------------------------------
### Main function and is called when the extension is run.

    
    def effect(self):

        #set up path styles
        path_stroke = '#DD0000' # take color from tab3
        path_fill   = 'none'     # no fill - just a line
        path_stroke_width  = 1. # can also be in form '0.6mm'
        page_id = self.options.active_tab # sometimes wrong the very first time
        
        style_curve = { 'stroke': path_stroke,
                 'fill': 'none',
                 'stroke-width': path_stroke_width }
        
        styles = [ { 'stroke': 'none', 'fill': '#000000', 'stroke-width': 0 },
                   { 'stroke': 'none',  'fill': '#FFFF00', 'stroke-width': 0 }]
        
        styles = [simplestyle.formatStyle(x) for x in styles]

        

        # This finds center of current view in inkscape
        t = 'translate(%s,%s)' % (self.view_center[0], self.view_center[1] )
        
        # Make a nice useful name
        g_attribs = { inkex.addNS('label','inkscape'): 'zengon' + "_%d_%.2f"%(self.options.depth,self.options.shrink_ratio),
                      inkex.addNS('transform-center-x','inkscape'): str(0),
                      inkex.addNS('transform-center-y','inkscape'): str(0),
                      'transform': t,
                      'style' : styles[1],
                      'info':'N: '+str(self.options.depth)+'; shrink:'+ str(self.options.shrink_ratio) }
        # add the group to the document's current layer
        topgroup = inkex.etree.SubElement(self.current_layer, 'g', g_attribs )


        # Add the zengram curve or group if filled
        if not self.options.mk_filled:
            
            curve_data = zengon(t =  .25*self.options.shrink_ratio,
                depth=self.options.depth,
               base_triangle = [0,200,200J],
               edges=self.options.mk_edges)
    
            curve_attribs = { inkex.addNS('label','inkscape'): 'zengram',
                              'style': simplestyle.formatStyle(style_curve),
                              'd': curve_data }
            
            inkex.etree.SubElement(topgroup,
                                    inkex.addNS('path','svg'),
                                    curve_attribs )
        else:
            
            #generate a list of nested triangles
            tris = zen_tris(t=.25*self.options.shrink_ratio,
                        depth=self.options.depth,
                base_triangle = [0,200,200J] )
                        
            tri_template = "M %.2f %.2f L %.2f, %.2f %.2f, %.2f Z"
            
            #add the first triangle with background color
            curve_attribs = { 'style': styles[0],
                                  'd': tri_template%tuple(cplxs2pts(tris[0]))}
            inkex.etree.SubElement(topgroup,
                                    inkex.addNS('path','svg'),
                                    curve_attribs )
            
            #add an new group to contain all the yellow triangles
            g_attribs = { inkex.addNS('label','inkscape'): 'zengon' + "_%d_%.2f"%(self.options.depth,self.options.shrink_ratio),
                      inkex.addNS('transform-center-x','inkscape'): str(0),
                      inkex.addNS('transform-center-y','inkscape'): str(0),
                      'style' : styles[1]
                      }
            
            midgroup = inkex.etree.SubElement(topgroup, 'g', g_attribs )
            
            for tri1,tri2 in zip(tris[1::2],tris[2::2]):

                tts  = [ [ tri2[0],tri1[1],tri2[1] ],
                        [ tri2[1],tri1[2],tri2[2] ],
                        [ tri2[-1],tri1[0],tri2[0] ]]
                
                for tri in tts:
                    inkex.etree.SubElement(midgroup,
                                         inkex.addNS('path','svg'),
                                        { 'd': tri_template%tuple(cplxs2pts(tri)) })
                    


if __name__ == '__main__':
    e = Myextension()
    e.affect()


