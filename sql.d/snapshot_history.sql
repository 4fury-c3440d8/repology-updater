-- Copyright (C) 2016-2018 Dmitry Marakasov <amdmi3@amdmi3.ru>
--
-- This file is part of repology
--
-- repology is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
--
-- repology is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with repology.  If not, see <http://www.gnu.org/licenses/>.

-- !!snapshot_history()

INSERT INTO repositories_history (
	ts,
	snapshot
)
SELECT
	now(),
	jsonb_object_agg(snapshot.name, to_jsonb(snapshot) - 'name')
FROM (
	SELECT
		name,
		num_metapackages,
		num_metapackages_unique,
		num_metapackages_newest,
		num_metapackages_outdated,
		num_metapackages_comparable,
		num_problems,
		num_maintainers
	FROM repositories
) AS snapshot;

INSERT INTO statistics_history (
	ts,
	snapshot
)
SELECT
	now(),
	to_jsonb(snapshot)
FROM (
	SELECT
		*
	FROM statistics
) AS snapshot;
