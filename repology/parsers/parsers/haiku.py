# Copyright (C) 2016-2018 Dmitry Marakasov <amdmi3@amdmi3.ru>
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
import re

from repology.logger import Logger
from repology.parsers import Parser


class HaikuPortsFilenamesParser(Parser):
    def iter_parse(self, path, factory, transformer):
        for category in os.listdir(path):
            category_path = os.path.join(path, category)
            if not os.path.isdir(category_path):
                continue

            for package in os.listdir(category_path):
                package_path = os.path.join(category_path, package)
                if not os.path.isdir(package_path):
                    continue

                for recipe in os.listdir(package_path):
                    if not recipe.endswith('.recipe'):
                        continue

                    pkg = factory.begin()

                    pkg.set_name(package)
                    pkg.add_categories(category)

                    # may want to shadow haiku-only ports
                    #if pkg.category.startswith('haiku-'):
                    #    pkg.shadow = True

                    # it seems to be guaranteed there's only one hyphen in recipe filename
                    name, version = recipe[:-7].split('-', 1)

                    if package.replace('-', '_') != name:
                        pkg.log('mismatch for package directory and recipe name: {} != {}'.format(package, name), severity=Logger.WARNING)

                    pkg.set_version(version)

                    # XXX: we rely on the fact that no substitutions happen in these
                    # variables. That's true as of 2018-05-14.
                    with open(os.path.join(category_path, package, recipe), 'r', encoding='utf-8') as recipefile:
                        match = re.search('^HOMEPAGE="([^"]+)"', recipefile.read(), re.MULTILINE)
                        if match:
                            pkg.add_homepages(match.group(1).split())

                    yield pkg
