from __future__ import division
import numpy as np
import cv2
import scipy
import pickle
import points

from sys import argv

ANTS = True
###HERE ARE THE PARAMETERS:::
####################################PARAMETERS FOR ANTSY.MP4
if ANTS:
    KERN_SIZE = 8
    RADIUS = 20
    THRESHOLD_AT = 100
    INPUT_SIZE_THRESHOLD = 75
    MINIMUM_PATH_SIZE = 10
    MINIMUM_PATH_STD = 3*RADIUS
    WRITE_TO_FILE = True
###END PARAMETERS
else:
    KERN_SIZE = 8
    RADIUS = 5
    THRESHOLD_AT = 127
    INPUT_SIZE_THRESHOLD = 150
    MINIMUM_PATH_SIZE = 10
    MINIMUM_PATH_STD = 3*RADIUS
    WRITE_TO_FILE = True

video_outputfile = "default_output.avi"

def avgit(x):
    return x.sum(axis=0)/np.shape(x)[0]
def plotp(p,mat,color=0):
    mat[p[0,1],p[0,0]] = color

if len(argv) != 3:
    cap = cv2.VideoCapture('evans1.mp4')
else:
    cap = cv2.VideoCapture(argv[1])
    video_outputfile = argv[2]
fourcc = cv2.VideoWriter_fourcc(*'XVID')
ret, frame = cap.read()
height, width, layers = frame.shape
video_out = cv2.VideoWriter(video_outputfile, fourcc, 30, (width, height), True)
print video_out.isOpened()

fgbg = cv2.createBackgroundSubtractorMOG2()
bwsub= cv2.createBackgroundSubtractorMOG2()

kernlen = KERN_SIZE
kern = np.ones((kernlen,kernlen))/(kernlen**2)
ddepth = -1
def blur(image):
    return cv2.filter2D(image,ddepth,kern)
def blr_thr(image, val=127):
    return cv2.threshold(blur(image),val,255,cv2.THRESH_BINARY)[1]
def normalize(image):
    s = np.sum(image)
    if s == 0:
       return image
    return height*width* image / s
#collection = []
paths = []
archive = []

r = RADIUS
thresh_at = THRESHOLD_AT
THIS_MUCH_IS_NOISE = INPUT_SIZE_THRESHOLD

while(cap.isOpened()):
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    fgmask = fgbg.apply(frame)
    mask = blur(fgmask)
    ret2, mask = cv2.threshold(mask, thresh_at, 255, cv2.THRESH_BINARY)
    
    res = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    cons = res[1]
    scatter = map(avgit, cons)
    filterWith = lambda x: len(x) > MINIMUM_PATH_SIZE and np.std(x) > MINIMUM_PATH_STD
    (toArchive, paths) = points.extendPaths(r, paths, scatter, filterWith, noisy=(len(scatter) > THIS_MUCH_IS_NOISE), discard=False)
    archive += toArchive
    img = (1 - mask)*gray
    #img = frame
    for path in archive:
        #color = 255
        cv2.polylines(img, np.int32([reduce(lambda x,y: np.append(x,y,axis=0), path)]), 0, (255,0,0))
        #for pnt in path:
        #    plotp(pnt, img, color=color)
    for path in paths:
        #color = 0
        cv2.polylines(img, np.int32([reduce(lambda x,y: np.append(x,y,axis=0), path)]), 1, (0,0,255))
        #for pnt in path:
        #    plotp(pnt, img, color=color)
    cv2.imshow('frame', img)
    video_out.write(img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
video_out.release()
cv2.destroyAllWindows()



if WRITE_TO_FILE:
    pickle.dump(archive, open('mypatharchive' + str(np.floor(1000*np.random.rand())) + '.pickle','w'))
