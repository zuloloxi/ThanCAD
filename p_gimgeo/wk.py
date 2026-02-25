from math import pi
from xml.sax.saxutils import escape
import p_ggen, p_ggeod


class ThanKmlWriter(object):
    "Creates and write a google Keyhole Markup Language file."
    header = """\
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>
    <name>%s</name>
    <Folder>
        <name>ThanCad</name>
"""
    formStyle = """\
        <Style id="%s">
            <IconStyle>
                <color>%s</color>
            </IconStyle>
            <LabelStyle>
                <color>%s</color>
            </LabelStyle>
        </Style>
"""
    formKmlcol = "ff%02x%02x%02x"
    dfn = "default_myplaces_style"     #Default value must exist
    formPlacemark = """\
       <Placemark>
           <name>%s</name>
           <description>%s</description>
           <styleUrl>#%s</styleUrl>
           <Point>
               <coordinates>%f,%f,%f</coordinates>
           </Point>
       </Placemark>
"""
    formLinestring = """\
       <Placemark>
           <name>%s</name>
           <description>%s</description>
           <styleUrl>#%s</styleUrl>
           <LineString>
               <tessellate>1</tessellate>
               <coordinates>
                   %s
               </coordinates>
           </LineString>
       </Placemark>
"""
    footer = """\
    </Folder>
</Document>
</kml>
"""

    def __init__(self, fw, name=""):
        "Write header of google Keyhole Markup Language file."
        if p_ggen.isString(fw):
            self.name = fw
            self.fw = open(self.name, "w")    #May raise IOError
        else:
            self.fw = fw
            try: self.name = fw.name
            except: self.name = name
            if self.name == "": self.name = "thancad"
        self.fw.write(self.header % (self.name,))
        self.writeLayer(self.dfn, (255,255,255))    #Default layer (style) with colour white
        self.projcur = p_ggeod.egsa87    #Default user geodetic projection


    def thanSetProjection(self, projection):
        """Set new user geodetic projection.

        The projection object must have the en2geodetGRS80(), geodetGRS802en() methods
        which transform user coordinates to GRS80 geodetic and vice versa."""
        assert projection != None, "Please use p_ggeod.GeodetGRS80() projection instead of None"
        self.projcur = projection


    def writeLayer(self, layer, colour):
        "Write a kml placemark style named layer and with rgb colour colour."
        t = self.formKmlcol % (colour[2], colour[1], colour[0])  #Google expects BRG (and not RGB)
        self.fw.write(self.formStyle % (layer, t, t))


    def writePlacemark(self, aa, cp, layer=dfn, desc=""):
        "Write a 3d point as a placemerk to a google Keyhole Markup Language file."
        al, phi = self.projcur.en2geodetGRS80(cp[0], cp[1])
        al  *= 180.0/pi
        phi *= 180.0/pi
        #aa = p_ggen.griso2utf(aa)
        #desc =  p_ggen.griso2utf(desc)
        self.fw.write(self.formPlacemark % (escape(aa), escape(desc), escape(layer), al, phi, cp[2]))


    def writeLinestring(self, aa, cp, layer=dfn, desc=""):
        "Write a line consisitng of 3d points as a linestring to a google Keyhole Markup Language file."
        temp = []
        for cpa in cp:
            al, phi = self.projcur.en2geodetGRS80(cpa[0], cpa[1])
            al  *= 180.0/pi
            phi *= 180.0/pi
            temp.append("%.14f,%.14f,%.14f" % (al, phi, cpa[2]))
        t = " ".join(temp)
        #aa = p_ggen.griso2utf(aa)
        #desc =  p_ggen.griso2utf(desc)
        self.fw.write(self.formLinestring % (escape(aa), escape(desc), escape(layer), t))


    def close(self):
        "Write footer of google Keyhole Markup Language file."
        self.fw.write(self.footer)
        self.fw.close()


def test1():
    "Write one point in EGSA87."
    dline = "1a1            285832.621    4216201.076        608.000  00000000    a1"
    aa, x, y, z, lay, desc = dline.split()
    x = float(x)
    y = float(y)
    z = float(z)
    kml = ThanKmlWriter("testw.kml")
    kml.writePlacemark(aa, (x, y, z), desc=desc)
    kml.close()


if __name__ == "__main__":
    test1()
