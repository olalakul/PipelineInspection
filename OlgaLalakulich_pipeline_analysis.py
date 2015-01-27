"""
@author: Olga Lalakulich (olalakul@gmail.com)
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
        self.id = self._ids.next()
        self._L = L #  left edge in meters
        self._length = length
        self._R = self._L + self._length # right edge in meters
        self._B = B #  bottom edge in degrees
        #self.T = (B + width)%360 #  top edge in degrees #curerntly not used
        self._width = width
        self._midangle = (self._B + self._width/2.)%360 # midangle in degrees # used for circumferential alignment
        if name=='':
            self.name="rect"+str(self.id)
        else:
            self.name = name


        @property
        def B(self):
            return self._B
            
        @B.setter
        def B(self, value):
            if not 0 <= value < 360:
                print("Your width is converted to the range from 0 to 360 degrees")
                value = value%360
            self._B = value

        @property
        def length(self):
            return self._length
            
        @length.setter
        def length(self, value):
            if 0 < length:
                raise ValueError("Length must be positive")
            self._L = value

        @property
        def width(self):
            return self._width
            
        @width.setter
        def width(self, value):
            if not 0 <= value < 360:
                raise ValueError("Width should be positive and less than 360")
            self._width = value




        
    def __repr__(self):
        """
        String representation for Rect
        """
        rep = "[Rectangle '" + self.name + "' with left edge " + str(self._L)
        rep += ", right edge " + str(self._R)
        rep += ", bottom edge " + str(self._B)
        rep += ", midangle " + str(self._midangle)
        rep += ", half-width " + str(self._width/2) + "]"
        return rep
        
    def to_the_left_of(self, another):
        """
        Returns True of self is to the left of other, else False
        Situations with "overlap" over a line or point are counted as True
        """
        return (self._R <= another._L)

    def to_the_right_of(self, another):
        """
        Returns True of self is to the left of other, else False
        Situations with "overlap" over a line or point are counted as True
        """
        return (self._L >= another._R)

    def overlap_along_circumferential(self, another):
        """
        Returns True of self and other overlap along circumferential axis, else False
        Situations with "overlap" over a line or point are counted as NOT-overlap
        >>> re5.overlap_along_circumferential(re6)
        True

        """
        dist_midangles = abs((self._midangle - another._midangle +180.)%360 -180)
        # overlap if distance between midangles is less than sum of half-widths
        return dist_midangles < (self._width + another._width)/2.

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
def overlap_between_two(old, new):
    """
    Finds rectangle overlaps between "old" and "new" containers of lengthes n and m.
    Complexity is O(n*log(n) + m*log(m)) and is dominated by sorting.
    If containers are naturally presorted (and sorting is removed from the algorithm),
    the complexity is O(m+n), quadratic in worst case (some rectangles are long)
    INPUTS:
    old - python container with rectangles
    new - another python container with rectangles
    OUTPUT:
    set of tuples with the names of rectangles in each overlapping pair
    >>> overlap_between_two([re5, re3, re1], [re4, re6, re2])
    set([('re1', 're2'), ('re5', 're6'), ('re5', 're2')])
    """
    from collections import deque
    # sort old  and new by left(L) coordinate
    list1 = sorted(old, key = lambda elem: elem._L)
    list2 = sorted(new, key = lambda elem: elem._L, reverse=True) # reverse for O(1) pop
    
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

    return overlap_set                
"""
This function can be suppelemented to produce during its run the 3D figure with 
each pair of overlapping rectangles (as in OlgaLalakulich-test.pdf). 
The code can be presented at the interview.
"""


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
The code can be presented at the interview.
"""
def overlap_between_two_left_right(old, new):
    pass

"""
Hire me. Contact e-mail: olalakul@gmail.com
"""

if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True, extraglobs={'re1': Rect(0,25, 5,25, "re1"),
                                              're2': Rect(5,20, 0,10, "re2"), 
                                              're3': Rect(10,10, 30,10, "re3"),
                                              're4': Rect(15,9, 40,20, "re4"),
                                              're5': Rect(20,10, 340,30, "re5"),
                                              're6': Rect(25,9, 0,10, "re6")})  

