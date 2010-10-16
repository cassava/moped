# Sets http://docs.python.org/3.1/library/stdtypes.html#set-types-set-frozenset
# ===================================
# id is some kind of search identifier, eg. artist or title
#     new A(id=filename as key) (init with list or set?)
#     
#     A.has_key(key) -> boolean
#     A.get_key(key) -> element or null
#     A.set_key(key, element)
#     A.del_key(key) -> element
#     
#     A.splice(id) -> (set or list) of sets
#     A.get_all(order="none", parameter="") -> list
#         #order= sort, shuffle, distribute, none
#         #parameter= w/ sort: id (default="filename")
#                     w/ shuffle: album, artist (default="")
#                     w/ distribute: id (default="artist")
# 
# these operations all work on other sets:
#     A.union(B) -> set
#     A.intersection(B) -> set
#     A.difference(B) -> set
#     
#     A.is_equal(B) -> boolean
#     A.is_subset(B) -> boolean
#     A.is_superset(B) -> boolean
#

# Get a set of all songs, and then manipulate that and search that
# That makes everything a lot more flexible albeit slower.

class SongSet():
    """SongSet defines various set operations on a set of songs"""
    
    def __init__(self, elements):
        """Initialize with a list of elements."""
        self.s = set(elements)
    
