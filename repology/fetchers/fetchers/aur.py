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
import urllib

from repology.fetchers import ScratchDirFetcher
from repology.fetchers.http import PoliteHTTP


def _split_names_into_urls(prefix, package_names, maxlen):
    url_parts = [prefix]
    url_length = len(prefix)

    for name in package_names:
        newpart = '&arg[]=' + urllib.parse.quote(name)

        if url_length + len(newpart) > maxlen:
            yield ''.join(url_parts), len(url_parts) - 1
            url_parts = [prefix, newpart]
            url_length = sum(map(len, url_parts))
        else:
            url_parts.append(newpart)
            url_length += len(newpart)

    if len(url_parts) > 1:
        yield ''.join(url_parts), len(url_parts) - 1


class AURFetcher(ScratchDirFetcher):
    def __init__(self, url, fetch_timeout=5, fetch_delay=None, max_api_url_length=4443):
        self.url = url
        self.do_http = PoliteHTTP(timeout=fetch_timeout, delay=fetch_delay)
        self.max_api_url_length = max_api_url_length  # see https://wiki.archlinux.org/index.php/Aurweb_RPC_interface#Limitations

    def _do_fetch(self, statedir, logger):
        packages_url = self.url + 'packages.gz'
        logger.GetIndented().Log('fetching package list from ' + packages_url)
        data = self.do_http(packages_url).text  # autogunzipped?

        package_names = []

        for line in data.split('\n'):
            line = line.strip()
            if line.startswith('#') or line == '':
                continue
            package_names.append(line)

        if not package_names:
            raise RuntimeError('Empty package list received, refusing to continue')

        logger.GetIndented().Log('{} package name(s) parsed'.format(len(package_names)))

        for num_page, (url, num_packages) in enumerate(_split_names_into_urls(self.url + '/rpc/?v=5&type=info', package_names, self.max_api_url_length)):
            logger.GetIndented().Log('fetching page {} of {} package(s)'.format(num_page + 1, num_packages))

            with open(os.path.join(statedir, '{}.json'.format(num_page)), 'wb') as statefile:
                statefile.write(self.do_http(url).content)
