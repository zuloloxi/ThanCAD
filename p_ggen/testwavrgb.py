from p_ggen import wavelen2rgb


for i in xrange(380, 781):
    r, g, b =  wavelen2rgb(float(i), 255.0)
    print i, r, g, b
