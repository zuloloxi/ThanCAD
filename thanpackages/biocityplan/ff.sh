#ffmpeg  -r 1 -b 1800 -i img_%04d.jpg -s cif q1.mp4
#ffmpeg  -r 1 -b 64k -i img_%04d.jpg -s xga q1.mp4
#ffmpeg -f image2 -i img_%04d.jpg -s xga q2.mpg
#ffmpeg  -r 1 -b 2000k -i evol%4d.jpg -s uxga q1.avi


ffmpeg  -r 20 -b 2000k -i evol%5d.jpg -s vga q1.avi
