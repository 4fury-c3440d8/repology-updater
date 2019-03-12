# Copyright (C) 2017-2019 Dmitry Marakasov <amdmi3@amdmi3.ru>
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

from typing import Generator

import lxml.html

from repology.packagemaker import PackageFactory, PackageMaker
from repology.parsers import Parser
from repology.transformer import PackageTransformer


class RudixHTMLParser(Parser):
    def iter_parse(self, path: str, factory: PackageFactory, transformer: PackageTransformer) -> Generator[PackageMaker, None, None]:
        for row in lxml.html.parse(path).getroot().xpath('.//table')[0].xpath('./tbody/tr'):
            pkg = factory.begin()

            pkg.set_name(row.xpath('./td[1]/a')[0].text)
            pkg.set_version(row.xpath('./td[2]')[0].text)
            pkg.set_summary(row.xpath('./td[3]')[0].text)
            pkg.add_licenses(row.xpath('./td[4]')[0].text)

            yield pkg
