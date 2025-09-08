import sys

import pyarrow
from osmium.osm import TagList

from .geoparquet import GeoParquetWriter


class PostalCodesWriter(GeoParquetWriter):
    COLUMNS = [
        ("postal_code", pyarrow.string()),
        # Some have a name instead of / in addition to a postal_code
        ("name", pyarrow.string()),
        ("type", pyarrow.string()),
    ]

    FILTERS = {"boundary"}

    def area(self, o):
        # NOTE: This check isn't super opinionated.
        # A postal code without a `postal_code` tag is not very useful,
        # but we won't filter such cases here in the interest of presenting a neutral view of OSM
        # and enabling validators to use the data set.
        if o.tags.get("boundary") != "postal_code":
            return

        try:
            self.append(
                "way" if o.from_way() else "relation",
                o.orig_id(),
                self.columns(o.tags),
                self.wkbfactory.create_multipolygon(o),
            )
        except RuntimeError as e:
            print(e, file=sys.stderr)

    def columns(self, tags: TagList):
        return {key: tags.get(key) for (key, _) in self.COLUMNS}
