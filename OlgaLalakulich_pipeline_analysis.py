"""
author: Olga Lalakulich (olalakul AT gmail.com)
Pipeline inspection. Example of Python code.
Problem.
--------
In pipeline inspection analysis, rectangular boxes are drawn to indicate regions 
that might contain anomalies. The location of the rectangular box is determined 
by its initial position in the longitudinal axis (in meters) and its initial 
position in the circumferential axis (in degrees). The length (in meters) and 
width (in degrees, from 0 to 360) of the boxes are also available. A new 
inspection run has been conducted on a pipeline (which was already inspected 
in the past) and new rectangular boxes have been drawn. We want to verify whether
the boxes from the new run and the boxes from the old run have the same location
in the pipeline. In other words, we want to check if one new box and one old box
overlap, not necessarily in all their area but at least in a portion of it. 
"""

"""
First I implement "Rect" class describing rectangular boxes
Two rectangles do NOT overlap if at least one of three conditions is satisfied:
1) rectangle under consideration (self) is completely to the left of another;
    that is the longitudinal coordinate of the Right edge of self is less than
    the longitudinal coordinate of the Left edge of another
    implemented as Rect.to_the_left_of(self, another)
2) rectangle under consideration is completely to the right of another
    implemented as Rect.to_the_right_of(self, other) 
3) rectangle under conderation fits "in-between" along the circumferencial axis;
    this is the case if the ciccumferential distance between the mid-angles of the
    two regtangles is less than the sum of their half-widths;
    The distance between mid-angles can be calculated as
    abs((self.midangle - another.midangle +180.)%360 -180)
    Negation of (3) is implemented as Rect.overlap_along_circumferential(self,another)
Two rectangles DO overlap if "not((1) or (2) or (3))"
    implemented as Rect.overlap_with(self, other)
"""

from itertools import count
class Rect:
    """
    Class for rectangular boxes on pipe
    """
    _ids = count(1)
    
    def __init__(self, L, length, B, width, name=''):
        """
        Create a rectangle based on 
        its initial position ("L" in meters along longitudinal axis, 
                              "B" in degrees from 0 to 360),
        its length ("length" in meters) and width ("width" in degrees )
        Please name your rectange ("name" as string).
        If not, name will be automatically generated.
        """
        assert 0<=B<=360, "initial position in the circumferencial axis should be between 0 and 360 degrees"
        assert length>0, "length should be positive"
        assert 0<=width<=360, "width should be between 0 and 360 degrees"
        self.id = self._ids.next()
        self.L = L #  left edge in meters
        self.R = L + length # right edge in meters
        self.B = B #  bottom edge in degrees
        #self.T = (B + width)%360 #  top edge in degrees #curerntly not used
        #self.length = length  # currently not used
        self.width = width
        self.midangle = (B+width/2.)%360 # midangle in degrees # used for circumferential alignment
        if name=='':
            self.name="rect"+str(self.id)
        else:
            self.name = name
        
    def __repr__(self):
        """
        String representation for Rect
        """
        rep = "[Rectangle '" + self.name + "' with left edge " + str(self.L)
        rep += ", right edge " + str(self.R)
        rep += ", bottom edge " + str(self.B)
        rep += ", midangle " + str(self.midangle)
        rep += ", half-width " + str(self.width/2) + "]"
        return rep
        
    def to_the_left_of(self, another):
        """
        Returns True of self is to the left of other, else False
        Situations with "overlap" over a line or point are counted as True
        """
        return (self.R <= another.L)

    def to_the_right_of(self, another):
        """
        Returns True of self is to the left of other, else False
        Situations with "overlap" over a line or point are counted as True
        """
        return (self.L >= another.R)

    def overlap_along_circumferential(self, another):
        """
        Returns True of self and other overlap along circumferential axis, else False
        Situations with "overlap" over a line or point are counted as NOT-overlap
        >>> re5.overlap_along_circumferential(re6)
        True
        """
        dist_midangles = abs((self.midangle - another.midangle +180.)%360 -180)
        # overlap if distance between midangles is less than sum of half-widths
        return dist_midangles < (self.width + another.width)/2.

    def overlap_with(self, another):
        """
        Returns True if rectangle overlaps with another rectangle
        Situations with "overlap" over a line or point are counted as NOT-overlap
        >>> re1.overlap_with(re2)
        True
        >>> re1.overlap_with(re3)
        False
        >>> re3.overlap_with(re2)
        False
        >>> re3.overlap_with(re4)
        False
        >>> re5.overlap_with(re4)
        False
        >>> re5.overlap_with(re6)
        True
        """
        return ( not(self.to_the_left_of(another)) and  
                 not(self.to_the_right_of(another)) and  
                 self.overlap_along_circumferential(another) )

    #def __eq__(self, another):
    #        return self.id == another.id


"""
For comparison of rectangles from the "old" and "new" runs, the simplest and ineffective 
version  is greedy algorithm. Its has quadratic complexity and is shown in the code 
(greedy_overlap_between_two(old, new))  for demonstration purpose only
"""
def greedy_overlap_between_two(old, new):
    """
    Greedy algorithm that checks if each rect from "old" overlaps with each one from "new"
    With m and n rectangulars in each container, complexity is O(m*n)
    Implemented for the demonstration purpose only
    Inefficient for long pipes with many rectangles along the pipe
    INPUTS:
    old - python container with rectangles
    new - another python container with rectangles
    OUTPUT:
    set of tuples with the names of rectangles in each overlapping pair
    >>> greedy_overlap_between_two([re5, re3, re1], [re4, re6, re2])
    set([('re5', 're6'), ('re1', 're2'), ('re5', 're2')])
    """
    overlap_set = set([])
    for rect in old:
        for another in new:
            if rect.overlap_with(another):
                overlap_set.add((rect.name,another.name))
    return overlap_set
                

"""
For the following technical situation
* number of rectangles (n and m) are large and growing with the length of the pipe
* not many rectangles along circumferential axis for a a fixed longitudinal coordinate
* all rectangles are not long and are of comparable length
I propose the following logic
1) sort "old" and "new" separately in increasing (strictly speaking, non-decreasing) order 
with respect to the left edge of each rectangle. This is O(n*log(n) + m*log(m)) operation
unless "old" and "new" are naturally presorted.
2) loop through the "old" and maintain a queue of candidates (those overlapping along longitudinal axis) 
from the "new".  Append to the queue those rectangles which are and not to the right 
and remove those which are to the left
3) check the current rectangle (which comes from the "old") with each one in the queue 
for overlapping  in circumferential direction
Implemented as overlap_between_two(old, new)
"""
def overlap_between_two(old, new, visualize=True):
    """
    Finds rectangle overlaps between "old" and "new" containers of lengthes n and m.
    Complexity is O(n*log(n) + m*log(m)) and is dominated by sorting.
    If containers are naturally presorted (and sorting is removed from the algorithm),
    the complexity is O(m+n), quadratic in worst case (some rectangles are long)
    INPUTS:
    old - python container with rectangles
    new - another python container with rectangles
    visualize - if True, produce 3D figure with  each pair of overlapping rectangles
    OUTPUT:
    set of tuples with the names of rectangles in each overlapping pair
    >>> overlap_between_two([re5, re3, re1], [re4, re6, re2], visualize=False)
    set([('re1', 're2'), ('re5', 're6'), ('re5', 're2')])
    """
    from collections import deque
    import matplotlib.pyplot as plt
    import mpl_toolkits.mplot3d
    import numpy as np
    
    if visualize:
        def xyz(phi1,phi2, h1,h2):
            phi = np.linspace(phi1,phi2, 100)
            r = np.ones(100)*10.
            h = np.linspace(h1,h2,100)
            y = np.outer(np.cos(phi),r)     
            z = np.outer(np.sin(phi),r)     
            x = np.outer(np.ones(np.size(r)),h)
            return x,y,z
            
        fig = plt.figure()
        ax = mpl_toolkits.mplot3d.Axes3D(fig)
        ax.view_init(200,260)
        x,y,z = xyz(0,2*np.pi,0,100)
        ax.plot_surface(x,y,z,rstride=5, cstride=10, linewidth=1, color='white', alpha=0.1)    
    
    
    # sort old  and new by left(L) coordinate
    list1 = sorted(old, key = lambda elem: elem.L)
    list2 = sorted(new, key = lambda elem: elem.L, reverse=True) # reverse for O(1) pop
    
    overlap_set = set([]) # set to store overlapping rectangles
    q2 = deque() # queue to store candidates (those horizontally overlapped with element in list1)
    # loop through "old"    
    for rect in list1:
        # remove candidate from the queue if it is to the left of rect
        while q2:
            if q2[0].to_the_left_of(rect):
                q2.popleft()
            else:
                break # because queue is sorted longitudinally, no need to check further
        # add element from list2 to the queue and pop from the list2 if longitudinal overlap with rect
        while list2:
            if list2[-1].to_the_left_of(rect): # it will also be to the left of others in list1 
                list2.pop() # remove those to the left of rect
            elif list2[-1].to_the_right_of(rect):
                break # because list2 is sorted longitudinally, no need to check further
            else: 
                elem = list2.pop()
                q2.append(elem)
        # check rect with each element in the queue and add to the overlap_set if they overelap       
        for elem in q2:
            if rect.overlap_along_circumferential(elem):
                overlap_set.add((rect.name, elem.name)) # add to the set if overlap
                # add visulization
                if visualize:
                    x1,y1,z1 = xyz(np.radians(rect.B),np.radians(rect.B+rect.width),rect.L,rect.R)
                    x2,y2,z2 = xyz(np.radians(elem.B),np.radians(elem.B+elem.width),elem.L,elem.R)
                    ax.plot_surface(x1,y1,z1,linewidth=0, color='red', alpha=0.5)
                    ax.plot_surface(x2,y2,z2,linewidth=0, color='blue', alpha=0.5)
                    fig.show()
    return overlap_set                


"""
For the following technical situation
* n>>m, that is  many rectangles in "old", few in "new"
* not many rectangles along circumferential axis for a a fixed longitudinal coordinate
* rectangles may significantly vary in length
1) Keep two sorted lists if "old": with respect to the left edge and to the right edge
2) Loop through the "new"; for each in the "new" search (binary search) those 
not-to-the-left of the current (using right-edge-sorted list) and those not-to-the-right 
of the current (using left-edge-sorted list). Intersection of found are candidates.
3) Check each candidate for overlapping with current in circumferential direction.
"""
def overlap_between_two_left_right(old, new):
    """
    >>> re1 = Rect(0,25, 5,25, "re1"); re2 = Rect(5,20, 0,10, "re2"); re3 = Rect(10,10, 30,10, "re3")
    >>> re4 = Rect(15,9, 40,20, "re4"); re5 = Rect(20,10, 340,30, "re5"); re6 = Rect(25,9, 0,10, "re6")
    >>> list1 = [re5, re3, re1];  list2 = [re4, re6, re2]
    >>> overlap_between_two_left_right(list1, list2)
    set([('re6', 're5'), ('re2', 're1'), ('re2', 're5')])
    """
    import bisect
    # sort old  by the left edge and then separately by the right
    old_left = sorted(old, key = lambda elem: elem.L)
    left_edges = [j.L for j in old_left]
    old_right = sorted(old, key = lambda elem: elem.R)
    right_edges = [j.R for j in old_right]    
    
    overlap_set = set([]) # set to store overlapping rectangles
    candidates_set = set([])
    # loop through "new"    
    for rect in new:
        # above this index, rect is to the left of others # O(log(n))
        il = bisect.bisect_left(left_edges, rect.R)
        # below this index, rect is to the right of others  # O(log(n))
        ir = bisect.bisect_right(right_edges, rect.L)
        # candidates are intersection of those not to the left and not to the right
        candidates_set = set(old_left[:il]).intersection(set(old_right[ir:]))
        #
        for elem in candidates_set:
            if rect.overlap_along_circumferential(elem):
                overlap_set.add((rect.name, elem.name)) # add to the set if overlap

    return overlap_set                


#re1 = Rect(0,25, 5,25, "re1"); re2 = Rect(5,20, 0,10, "re2"); re3 = Rect(10,10, 30,10, "re3")
#re4 = Rect(15,9, 40,20, "re4"); re5 = Rect(20,10, 340,30, "re5"); re6 = Rect(25,9, 0,10, "re6")
#list1 = [re5, re3, re1];  list2 = [re4, re6, re2]
#list3 = [re5, re1, re4];  list4 = [re3, re2, re6]
#overlap_between_two_left_right(list3, list4)
#overlap_between_two(list1, list2, visualize=False)
#greedy_overlap_between_two(list3, list4)

"""
Hire me. Contact e-mail: olalakul AT gmail.com
"""
if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True, extraglobs={'re1': Rect(0,25, 5,25, "re1"),
                                              're2': Rect(5,20, 0,10, "re2"), 
                                              're3': Rect(10,10, 30,10, "re3"),
                                              're4': Rect(15,9, 40,20, "re4"),
                                              're5': Rect(20,10, 340,30, "re5"),
                                              're6': Rect(25,9, 0,10, "re6")})  

