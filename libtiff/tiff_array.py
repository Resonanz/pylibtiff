""" Implements an array of TIFF sample images.
"""
# Author: Pearu Peterson
# Created: Nov 2010

from __future__ import division
import sys
import numpy

__all__ = ['TiffArray']

class TiffArray:
    """ Holds a sequence of homogeneous TiffPlane's.

    TiffPlane's are homogeneous if they contain sample images of same
    shape and type. Otherwise TiffPlane's may contain images from
    different TIFF files with different pixel content.
    """
    def __init__ (self, planes):
        self.planes = []
        self.shape = ()
        self.dtype = None
        map(self.append, planes)

    def __len__(self):
        return self.shape[0]

    def __getitem__ (self, index):
        try:
            if isinstance(index, (int, long)):
                if self.sample_index is None:
                    print self.shape
                return self.planes[index][()]
            elif isinstance (index, slice):
                indices = range (*index.indices(self.shape[0]))
                r = numpy.empty((len(indices),)+self.shape[1:], dtype=self.dtype)
                for i,j in enumerate(indices):
                    r[i] = self.planes[j][()]
                return r
            elif isinstance(index, tuple):
                if len (index)==0:
                    return self[:]
                if len (index)==1:
                    return self[index[0]]
                index0 = index[0]
                if isinstance(index0, (int, long)):
                    return self.planes[index0][index[1:]]
                elif isinstance (index0, slice):
                    indices = range (*index0.indices(self.shape[0]))
                    for i,j in enumerate(indices):
                        s = self.planes[j][index[1:]]
                        if i==0:
                            r = numpy.empty((len(indices),)+s.shape, dtype=self.dtype)
                        r[i] = s
                    return r
        except IOError, msg:
            sys.stderr.write('%s.__getitem__:\n%s\n' % (self.__class__.__name__, msg))
            sys.stderr.flush ()
            return None
        raise NotImplementedError (`index`)

    def append(self, plane):
        """ Append tiff plane to tiff array.
        """
        if self.planes:
            if not self.planes[0].check_same_shape_and_type (plane):
                raise TypeError('planes are not homogeneous (same shape and sample type), expected %s but got %s' % ((self.planes[0].shape, self.dtype), (plane.shape, plane.dtype)))
            self.shape = (self.shape[0]+1,) + self.shape[1:]
        else:
            self.dtype = plane.dtype
            self.shape = (1,) + plane.shape
            self.sample_index = plane.sample_index
        self.planes.append(plane)

    def extend(self, other):
        """ Extend tiff array with the content of another.
        """
        map(self.append, other.planes)
              
    def get_voxel_sizes(self):
        """ Return ZYX voxel sizes in microns.
        """
        return self.planes[0].ifd.get_voxel_sizes()

    def get_pixel_sizes(self):
        """ Return YX pixel sizes in microns.
        """
        return self.planes[0].ifd.get_pixel_sizes()

    def get_time(self, index = 0):
        """ Return time parameter of a plane.
        """
        return self.planes[index].time

    @property
    def nbytes(self):
        return self.shape[0] * self.shape[1] * self.shape[2] * self.dtype.itemsize
