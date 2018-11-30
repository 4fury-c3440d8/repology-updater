# Copyright (C) 2018 Dmitry Marakasov <amdmi3@amdmi3.ru>
#
# This file is part of repology
#
# repology is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# repology is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with repology.  If not, see <http://www.gnu.org/licenses/>.

import os


__all__ = ['walk_tree']


def walk_tree(path, filt=None, suffix=None, name=None):
    if suffix:
        def suffix_filter(filename):
            return filename.endswith(suffix)
        filt = suffix_filter
    elif name:
        def name_filter(filename):
            return filename == name
        filt = name_filter

    for root, _, files in os.walk(path):
        for filename in files:
            if filt and not filt(filename):
                continue

            yield os.path.join(root, filename)
