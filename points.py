import numpy as np
import numpy.linalg.linalg as la
import matplotlib.pyplot as plt

fst = lambda x: x[0]
snd = lambda x: x[1]

distance = lambda p1,p2: la.norm(p1 - p2)

matchPaths = lambda r, a, paths: [neighborhoodPath(r,paths,ai) for ai in a]

neighborhoodPath = lambda r, paths, pnt: [path for path in paths if distance(path[0],pnt) < r]

def itemMatcher(choice, items):
    items = list(sorted(items, key = lambda x: len(x[1])))
    accumulator = []
    #for (a, bs) in items:
    for index in range(len(items)):
        (a, bs) = items[index]
        if bs == []:
            accumulator.append((a, None))
        else:
            b = choice(a,bs)
            accumulator.append((a, b))
            #removing b
            for ind in range(len(items)):
                (a2, bs2) = items[ind]
                if any(np.array_equal(b,belement) for belement in bs):
                    #bs2.remove(b)
                    bs2 = [belement for belement in bs2 if not np.array_equal(belement, b)]
                items[ind] = (a2, bs2)
    return accumulator


def extendPaths(r, paths, scatter, filterWith, noisy = False, discard = True): #filterWith = (lambda x: len(x) > 10 and np.std(x) > 3*r)):
    matches = matchPaths(r,scatter,paths)
    zipped = zip(scatter, matches)
    def choice(point, pathOptions): 
        #endpoints = [ opt[0] for opt in pathOptions]
        #return  fst(min(zip(pathOptions,([distance(point,ep) for ep in endpoints])),key=snd))
        return max(pathOptions,key=len)
    def combine(tup):
        (pnt, val) = tup
        if val == None:
            ##Only turn this to a new path if the region is not noisy
            if not noisy:
                return [pnt]
            else:
                return []
        else:
            return [pnt] + val
    lst = itemMatcher(choice, zipped)
    #DO NOT THROW AWAY PATHS THAT HAVE NO CONTINUATION!!!!!!!!!!!!!!!!!!!!!!!!!!!
    extended_paths = map(snd,lst)
    if discard:
       return filter(lambda x: x != [], map(combine,lst))
    unextended_paths = [p for p in paths if not array_in(p,extended_paths)] #OOPS!!
    unextended_paths = filter(filterWith, unextended_paths)
    #return filter(lambda x: x!=[], unextended_paths + [combine(elem) for elem in lst])
    return ( unextended_paths, filter(lambda x: x!=[], map(combine, lst)) ) # First element is paths to be archived, second element is the extended paths
   

def array_in(arr, lst):
    return any(np.array_equal(arr,elem) for elem in lst)

import pickle
def loaddata(filename):
    return pickle.load(open(filename))

def stringPaths(r, scatters):
    paths = []
    for sc in scatters:
        paths = extendPaths(r, paths, sc)
    return paths

def plotit(paths):
    p = [reduce(lambda x,y: np.append(x,y,axis=0),pa) for pa in paths]
    p = map(lambda x: x.T, p)
    plt.hold(True)
    map(lambda x: plt.plot(x[0],x[1],'x'),p)

def shortcut(r, filename):
    plotit(stringPaths(r, loaddata(filename)))
def rawpoints(filename):
    scatters = loaddata(filename)
    plotit(scatters)
