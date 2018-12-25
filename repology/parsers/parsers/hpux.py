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

from repology.parsers import Parser


class HPPADepothelperListParser(Parser):
    def iter_parse(self, path, factory, transformer):
        with open(path, encoding='utf-8') as indexfile:
            for line in indexfile:
                pkg = factory.begin()

                pkgname, pkgpath = line.strip().split('|')[:2]

                pkg.set_name_and_version(pkgname)
                pkg.set_extra_field('path', pkgpath)

                yield pkg
