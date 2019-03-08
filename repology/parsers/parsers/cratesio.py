# Copyright (C) 2017-2018 Dmitry Marakasov <amdmi3@amdmi3.ru>
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
import os
from typing import Generator

from repology.packagemaker import PackageFactory, PackageMaker
from repology.parsers import Parser
from repology.transformer import PackageTransformer


class CratesIOParser(Parser):
    def iter_parse(self, path: str, factory: PackageFactory, transformer: PackageTransformer) -> Generator[PackageMaker, None, None]:
        for pagefilename in os.listdir(path):
            if not pagefilename.endswith('.json'):
                continue

            pagepath = os.path.join(path, pagefilename)

            with open(pagepath, 'r', encoding='utf-8', errors='ignore') as pagedata:
                for crate in json.load(pagedata)['crates']:
                    pkg = factory.begin()

                    pkg.set_name(crate['id'])
                    pkg.set_version(crate['max_version'])

                    pkg.set_summary(crate['description'])

                    pkg.add_homepages(crate['homepage'])
                    pkg.add_homepages(crate['repository'])

                    yield pkg
