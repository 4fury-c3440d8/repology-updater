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

import importlib
import importlib.util
import inspect
import os
from typing import Any, Dict, Generator, Optional, Type


__all__ = [
    'ClassFactory',
]


class ClassFactory:
    @staticmethod
    def _enumerate_all_submodules(module: str) -> Generator[str, None, None]:
        spec = importlib.util.find_spec(module)
        if spec is None:
            raise RuntimeError('cannot find module {}'.format(module))
        if spec.submodule_search_locations is None:
            raise RuntimeError('module {} is not a package'.format(module))

        for location in spec.submodule_search_locations:
            for dirpath, dirnames, filenames in os.walk(location):
                for filename in filenames:
                    fullpath = os.path.join(dirpath, filename)
                    relpath = os.path.relpath(fullpath, location)

                    if not filename.endswith('.py'):
                        continue

                    yield '.'.join([module] + relpath[:-3].split(os.sep))

    def __init__(self, modulename: str, suffix: Optional[str] = None, superclass: Optional[Type[Any]] = None) -> None:
        self.classes: Dict[str, Any] = {}

        for submodulename in ClassFactory._enumerate_all_submodules(modulename):
            submodule = importlib.import_module(submodulename)
            for name, member in inspect.getmembers(submodule):
                suitable = True

                if suffix is not None:
                    suitable &= name.endswith(suffix)

                if superclass is not None:
                    suitable &= inspect.isclass(member) and issubclass(member, superclass)

                if suitable:
                    self.classes[name] = member

    def Spawn(self, name: str, *args: Any, **kwargs: Any) -> Any:
        return self.classes[name](*args, **kwargs)

    def SpawnWithKnownArgs(self, name: str, kwargs: Dict[str, Any]) -> Any:
        class_ = self.classes[name]

        filtered_kwargs = {
            key: value for key, value in kwargs.items() if key in inspect.getfullargspec(class_.__init__).args
        }

        return class_(**filtered_kwargs)
