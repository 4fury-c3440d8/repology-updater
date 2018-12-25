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

from repology.logger import Logger
from repology.parsers import Parser
from repology.parsers.maintainers import extract_maintainers
from repology.parsers.versions import VersionStripper


class PkgsrcIndexParser(Parser):
    def iter_parse(self, path, factory, transformer):
        normalize_version = VersionStripper().strip_right('nb')

        with open(path, encoding='utf-8') as indexfile:
            for line in indexfile:
                pkg = factory.begin()

                fields = line.strip().split('|')
                if len(fields) != 12:
                    pkg.log('skipping, unexpected number of fields {}'.format(len(fields)), severity=Logger.ERROR)
                    continue
                if not fields[0]:
                    pkg.log('skipping, empty first field', severity=Logger.ERROR)
                    continue

                pkg.set_name_and_version(fields[0], normalize_version)
                pkg.set_summary(fields[3])

                # sometimes OWNER variable is used in which case
                # there's no MAINTAINER OWNER doesn't get to INDEX
                pkg.add_maintainers(extract_maintainers(fields[5]))

                pkg.add_categories(fields[6].split())
                pkg.add_homepages(fields[11])

                pkg.set_extra_field('portname', fields[1].split('/')[-1])
                pkg.set_origin(fields[1])

                yield pkg
