"""This module implements methods missing from the micropython os module API.
"""

import os
from collections import namedtuple


S_IFDIR = 0o40000

StatStruct = namedtuple('StatStruct', (
    'st_mode',
    'st_ino',
    'st_dev',
    'st_nlink',
    'st_uid',
    'st_gid',
    'st_size',
    'st_atime',
    'st_mtime',
    'st_ctime',
))

StatVfsStruct = namedtuple('StatVfsStruct', (
    'f_bsize',
    'f_frsize',
    'f_blocks',
    'f_bfree',
    'f_bavail',
    'f_files',
    'f_ffree',
    'f_favail',
    'f_flag',
    'f_namemax',
))



stat = lambda path: StatStruct(*os.stat(path))

statvfs = lambda path: StatVfsStruct(*os.statvfs(path))


class path():


    @staticmethod
    def isdir(path):
        return bool(stat(path).st_mode & S_IFDIR)


    @staticmethod
    def exists(path):
        """Return a bool indicating whether the specified path exists by trying
        to to stat() it because the upython os module has no exists().
        """
        try:
            os.stat(path)
        except OSError:
            return False
        else:
            return True


    @staticmethod
    def getsize(path):
        """Return the size in bytes of the path.
        """
        return stat(path).st_size


    @staticmethod
    def join(*args):
        return '/'.join(args).replace('//', '/')


    @staticmethod
    def split(path):
        return path.split('/')
