import p_ggen, p_gnum


def histogramAuto(band, per=0.01):
    "Compute the histogram for elevations stored in a list (band); automatically find hmin and hmax."
    hmin = min(band)
    hmax = max(band)
    freq, width = histogram(band, hmin, hmax, 4096)  #A large number of bins
    hmin, hmax = approx(freq, per)
    return histogram(band, hmin, hmax)


def histogram(band, hmin, hmax, n=100):
    "Compute the histogram for elevations stored in a list (band) for elevation between hmin and hmax."
    #n is the number of bins
    hmin += 0.0     #Convert to real
    hmax += 0.0     #Convert to real
    print("hmin=", hmin, "hmax=", hmax)
    dh = (hmax-hmin)/n
    bins = list(p_ggen.frangec(hmin, hmax, dh))
    print("number of bins=", len(bins))
    fre, _ = p_gnum.histogram(band, bins, (hmin, hmax))
    #freq = zip(range(n), h)
    h = [(xa+xb)*0.5 for xa, xb in p_ggen.iterby2(bins)]
    freq = list(zip(h, fre))    #OK for python 2,3
    #print freq
    width = bins[1]-bins[0]     #The (constant) width of one bin
    return freq, width


def approx(freq, per=0.01):
    "Find an initial approximation of position and size, inspecting histograms."
    #per = Percentage of least importance; per*max frequency is the frequency importance threshold
    fmax = max(f for h,f in freq)
    fmin = per*fmax       #Elevations with smaller frequency than this are of no importance
    print("frequency threshold=", fmin)
    for i in range(len(freq)):
        h, f = freq[i]
        if f >= fmin: break  #Note that this condition will be true for at least once (for f=fmax)
    h1 = h            #Smallest eleveation with frequence larger or equal to the frequency threshold
    print("h1, frequency", h1, f)
    for i in range(len(freq)-1, -1, -1):
        h, f = freq[i]
        if f >= fmin: break
    h2 = h            #Smallest eleveation with frequence larger or equal to the frequency threshold
    print("h2, frequency", h2, f)
    return h1, h2


def histogramShow(freq, width, fim):
    import matplotlib.pyplot as plt
    width = 0.7 * width
    center = [a[0] for a in freq]
    f = [a[1] for a in freq]
    plt.bar(center, f, align='center', width=width)
    plt.savefig(fim)


def test():
    "Test with a DEM."
    from PIL import Image
    im = Image.open("tanidem5.tif")
    hs = p_gnum.im2num(im)
    hs = hs.reshape((hs.shape[0]*hs.shape[1],))
    hs = [h for h in hs if h != -999999 and int(h*1000) != 0]
    hmin = min(hs)
    hmax = max(hs)
    freq, width = histogram(hs, hmin, hmax)
    histogramShow(freq, width, "bar1.png")
    freq, width = histogramAuto(hs)
    histogramShow(freq, width, "bar2.png")


if __name__ == "__main__":
    test()
