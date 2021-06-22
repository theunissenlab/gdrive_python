"""
Wrappers for displaying pydrive results nicely
"""

from pydrive2.files import GoogleDriveFile


def _file_to_string(self):
    try:
        return "{title}\n\t{mimeType}".format(**self)
    except:
        return super(GoogleDriveFile, self).__repr__()


class PyDriveListWrapper(list):
    def __repr__(self):
        if not len(self):
            return "<folder empty>"

        return "\n".join([
            "{}: {}".format(i, f) for i, f in enumerate(self)
        ]) + "\n{}".format(type(self))

    def __add__(self, other):
        if not isinstance(other, PyDriveListWrapper):
            raise TypeError("Cannot add object of type {} to PyDriveListWrapper".format(type(other)))

        return PyDriveListWrapper(super().__add__(other))


GoogleDriveFile.__repr__ = _file_to_string


__all__ = ["PyDriveListWrapper"]
