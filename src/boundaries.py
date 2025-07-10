import sys

import pyarrow
from osmium.osm import TagList

from .geoparquet import GeoParquetWriter


class BoundariesWriter(GeoParquetWriter):
    TAGS = [
        "name",
        ("multilingual_names", pyarrow.map_(pyarrow.string(), pyarrow.string())),
        "type",
        "admin_level",
        "boundary",
        "place",
        "ISO3166-2",
        "ISO3166-1:alpha2",
        "ISO3166-1:alpha3",
    ]

    FILTERS = {"boundary"}

    def __init__(self, filename):
        super().__init__(filename, self.TAGS)

    def area(self, o):
        if o.tags.get("boundary") not in {
            "administrative",
            "maritime",
            "disputed",
            "place",
        }:
            return

        try:
            self.append(
                "way" if o.from_way() else "relation",
                o.orig_id(),
                process_tags(o.tags),
                self.wkbfactory.create_multipolygon(o),
            )
        except RuntimeError as e:
            print(e, file=sys.stderr)


def process_tags(tags: TagList):
    # Preserve the basic tags as-is
    # TODO: alt names?
    res = {tag.k: tag.v for tag in tags if not tag.k.startswith("name:")}

    # Special shape transformation for names
    name_tags = {tag.k: tag.v for tag in tags if tag.k.startswith("name:")}

    res["multilingual_names"] = name_tags
    return res
