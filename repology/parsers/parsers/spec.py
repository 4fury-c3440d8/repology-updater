# Copyright (C) 2016-2017 Dmitry Marakasov <amdmi3@amdmi3.ru>
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

from repology.parsers import Parser


class SpecParser(Parser):
    def iter_parse(self, path, factory):
        for root, _, files in os.walk(path):
            for filename in files:
                if not filename.endswith('.spec'):
                    continue

                with open(os.path.join(root, filename), encoding='utf-8', errors='ignore') as specfile:
                    pkg = factory.begin(filename)

                    for line in specfile:
                        line = line.strip()

                        if '%' in line:  # substitudes: ignore
                            continue

                        if line.startswith('Name:') and not pkg.name:
                            pkg.set_name(line.split(':', 1)[1])
                        elif line.startswith('Version:') and not pkg.version:
                            pkg.set_version(line.split(':', 1)[1])
                        elif line.startswith('Url:') and not pkg.homepage:
                            pkg.add_homepages(line.split(':', 1)[1])
                        elif line.startswith('License:') and not pkg.license:
                            pkg.add_licenses(line.split(':', 1)[1])
                        elif line.startswith('Group:') and not pkg.category:
                            pkg.add_categories(line.split(':', 1)[1])
                        elif line.startswith('Summary:') and not pkg.comment:
                            pkg.set_summary(line.split(':', 1)[1])

                    yield pkg
