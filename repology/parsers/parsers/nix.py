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

import json
import re

from repology.logger import Logger
from repology.package import PackageFlags
from repology.parsers import Parser
from repology.parsers.maintainers import extract_maintainers


def extract_nix_maintainers(items):
    for item in items:
        # old format, currently used in stable; parse email out of 'name <email>' string
        # items without closing '>' are quite common, just skip them
        if isinstance(item, str):
            for maintainer in extract_maintainers(item):
                if '<' not in maintainer:
                    yield maintainer
        elif isinstance(item, dict):
            yield item['email'].lower()
            # do we need these?
            #if 'github' in item:
            #    yield item['github'].lower() + '@github'


def extract_nix_licenses(whatever):
    if isinstance(whatever, str):
        return [whatever]
    elif isinstance(whatever, list):
        return sum(map(extract_nix_licenses, whatever), [])
    elif isinstance(whatever, dict) and 'spdxId' in whatever:
        return [whatever['spdxId']]
    elif isinstance(whatever, dict) and 'fullName' in whatever:
        return [whatever['fullName']]
    elif isinstance(whatever, dict) and 'fullname' in whatever:
        return [whatever['fullname']]
    else:
        #factory.log('unable to parse license {}'.format(whatever), severity=Logger.ERROR)
        return []


class NixJsonParser(Parser):
    def iter_parse(self, path, factory, transformer):
        with open(path, 'r', encoding='utf-8') as jsonfile:
            for key, packagedata in json.load(jsonfile)['packages'].items():
                pkg = factory.begin(key)

                # see how Nix parses 'derivative' names in
                # https://github.com/NixOS src/libexpr/names.cc, DrvName::DrvName
                # it just splits on dash followed by non-letter
                #
                # this doesn't work well on 100% cases, it's an upstream problem
                match = re.match('(.+?)-([^a-zA-Z].*)$', packagedata['name'])
                if not match:
                    factory.log('cannot extract version: {}/{}'.format(key, packagedata['name']), severity=Logger.ERROR)
                    continue

                pkg.set_name(match.group(1))
                pkg.set_version(match.group(2))

                # some exceptions
                for prefix in ('75dpi', '100dpi'):
                    if pkg.version.startswith(prefix):
                        pkg.set_name(pkg.name + '-' + prefix)
                        pkg.set_version(pkg.version[len(prefix) + 1:])

                merged = pkg.name + '-' + pkg.version
                for pkgname in ['liblqr-1', 'python2.7-3to2', 'python3.6-3to2', 'libretro-4do', 'polkit-qt-1-qt5', 'polkit-qt-1-qt4']:
                    if merged.startswith(pkgname):
                        pkg.set_name(pkgname)
                        pkg.set_version(merged[len(pkgname) + 1:])

                keyparts = key.split('.')
                if len(keyparts) > 1:
                    pkg.add_categories(keyparts[0])

                if pkg.name.endswith('-git'):
                    pkg.set_name(pkg.name[:-4])
                    pkg.set_flags(PackageFlags.ignore)

                if re.match('.*20[0-9]{2}-[0-9]{2}-[0-9]{2}', pkg.version):
                    pkg.set_flags(PackageFlags.ignore)

                if re.match('[0-9a-f]*[a-f][0-9a-f]*$', pkg.version) and len(pkg.version) >= 7:
                    pkg.log('ignoring version which looks like commit hash: {}'.format(pkg.version), severity=Logger.ERROR)
                    pkg.set_flags(PackageFlags.ignore)

                meta = packagedata['meta']

                pkg.add_homepages(meta.get('homepage'))

                if 'description' in meta:
                    pkg.set_summary(meta['description'].replace('\n', ' '))

                if 'maintainers' in meta:
                    if not isinstance(meta['maintainers'], list):
                        pkg.log('maintainers is not a list: {}'.format(meta['maintainers']), severity=Logger.ERROR)
                    else:
                        pkg.add_maintainers(extract_nix_maintainers(meta['maintainers']))

                if 'license' in meta:
                    pkg.add_licenses(extract_nix_licenses(meta['license']))

                if 'position' in meta:
                    posfile, posline = meta['position'].rsplit(':', 1)
                    pkg.set_extra_field('posfile', posfile)
                    pkg.set_extra_field('posline', posline)

                    if posfile.startswith('pkgs/development/haskell-modules'):
                        pkg.set_flags(PackageFlags.rolling)  # XXX: haskell modules are autogenerated in nix: https://github.com/NixOS/nixpkgs/commits/master/pkgs/development/haskell-modules/hackage-packages.nix

                yield pkg
