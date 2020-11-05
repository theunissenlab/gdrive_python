"""
Wrappers for displaying pydrive results nicely
"""

from pydrive.files import GoogleDriveFile


def _file_to_string(self):
    return "{title}\t\t{mimeType}\t{createdDate}\t{modifiedDate}".format(**self)


class PyDriveListWrapper(list):
    def __repr__(self):
        if not len(self):
            return "<folder empty>"

        return "\n".join([
            "{}:\t\t{}".format(i, f) for i, f in enumerate(self)
        ]) + "\n{}".format(type(self))


GoogleDriveFile.__repr__ = _file_to_string


__all__ = ["PyDriveListWrapper"]
