from observable import Transparant

def findHelix(dna, clazz):
    for strand in dna:

        component, observers = strand, []
        if type(strand) == tuple:
            component = strand[0]
            if len(strand) == 2:
                observers = strand[1]

        if type(component) == clazz:
            yield strand
        for helix in findHelix(observers, clazz):
            yield helix

def be(dna):
    handle = Transparant()
    handle.addObservers(dna)
    return handle
