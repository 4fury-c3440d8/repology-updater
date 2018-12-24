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

import json

from repology.package import PackageFlags
from repology.parsers import Parser


class SliTazJsonParser(Parser):
    def iter_parse(self, path, factory):
        with open(path, encoding='utf-8') as jsonfile:
            for item in json.load(jsonfile)['items']:
                pkg = factory.begin()

                pkg.set_basename(item['meta'])
                pkg.set_version(item['ver'])
                pkg.add_maintainers(item['maintainer'])
                pkg.add_licenses(item['license'])
                pkg.add_homepages(item['home'])
                pkg.add_downloads(item.get('src'))

                if pkg.version == 'latest':
                    pkg.set_flags(PackageFlags.rolling)

                for subitem in item['pkgs']:
                    subpkg = pkg.clone()

                    subpkg.add_categories(subitem['cat'])
                    subpkg.set_summary(subitem['desc'])
                    subpkg.set_name(subitem['name'])
                    subpkg.set_version(subitem.get('ver'))

                    yield subpkg
