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
import xml.etree.ElementTree

from repology.logger import Logger
from repology.parsers import Parser
from repology.parsers.walk import walk_tree


class PisiParser(Parser):
    def iter_parse(self, path, factory, transformer):
        for filename in walk_tree(path, suffix='pspec.xml'):
            relpath = os.path.relpath(filename, path)

            pkg = factory.begin(relpath)

            try:
                root = xml.etree.ElementTree.parse(filename)
            except xml.etree.ElementTree.ParseError as e:
                pkg.log('Cannot parse XML: ' + str(e), Logger.ERROR)
                continue

            pkg.set_name(root.find('./Source/Name').text)
            pkg.set_summary(root.find('./Source/Summary').text)
            pkg.add_homepages(map(lambda el: el.text, root.findall('./Source/Homepage')))
            pkg.add_downloads(map(lambda el: el.text, root.findall('./Source/Archive')))
            pkg.add_licenses(map(lambda el: el.text, root.findall('./Source/License')))
            pkg.add_categories(map(lambda el: el.text, root.findall('./Source/IsA')))
            pkg.add_maintainers(map(lambda el: el.text, root.findall('./Source/Packager/Email')))

            pkg.set_extra_field('pspecdir', os.path.dirname(relpath))

            lastupdate = max(root.findall('./History/Update'), key=lambda el: int(el.attrib['release']))
            pkg.set_version(lastupdate.find('./Version').text)

            yield pkg
