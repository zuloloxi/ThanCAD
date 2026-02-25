try:
    from osgeo import gdalconst
except ImportError:
    pass   #The call to readTerrasarBand will terminate the progran if convertTerrasar2Tif() is called
import p_ggen
from . import gdal_bands, hist


def convertTerrasar2Tif(infile, outfile=None, color16=False, manually=False, parent=None, prt=p_ggen.doNothing):
    "Convert TerraSAR complex .cos file to geotiff 16bit or 8bit grayscale."
    infile = p_ggen.path(infile)
    prt("Reading .cos image", "info1")
    band, size, terr = gdal_bands.readTerrasarBand(infile)
    if band is None:
        #print 'Cannot open', infile, ":", terr
        return None, terr
    prt("Converting from complex to 16bit integer pixels", "info1")
    band[0] = gdal_bands.convertComplex2Int16(band[0])

    if color16:
        if outfile is None: outfile = infile.parent / infile.namebase +".tif"
        prt("Saving 16bit GeoTiff image", "info1")
        gdal_bands.writeBands(band, size, outfile, gdalconst.GDT_UInt16)
        return outfile, ""

    ra = None
    if manually:
        if parent is None:
            import tkinter
            parent = tkinter.Tk()
        ra = hist.selectColourRange(band, parent) #This may return None, if use cancelled manually
        if ra[0] < 0: ra = 0, ra[1]
        print("ra=", ra)
    if ra is None:
        prt("Auto determining 8bit limits", "info1")
        h1 = hist.Hist()
        h1.fromArray(band[0])
        h1.statistics()
        ra = h1.approx()
        print("x1, x2=", ra[0], ra[1])

    prt("Converting to 8bit integer pixels", "info1")
    gdal_bands.convertCol16to8(band, ra[0], ra[1])
    if outfile is None: outfile = infile.parent / infile.namebase +"_8.tif"
    prt("Saving 8bit GeoTiff image", "info1")
    gdal_bands.writeBands(band, size, outfile, gdalconst.GDT_Byte)
    return outfile, ""


if __name__ == "__main__":
    infile = "image_hh_sra_spot_096.cos"
    fn, terr = convertTerrasar2Tif(infile, color16=False, manually=True)
    print("fn=", fn, "   terr=", terr)
