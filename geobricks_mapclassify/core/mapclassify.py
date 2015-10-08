import uuid
import os
from geobricks_common.core.log import logger
from geobricks_common.core.utils import dict_merge
from geobricks_mapclassify.core.sld import create_sld_xml
from geobricks_mapclassify.core.colors import get_colors
from geobricks_mapclassify.core.classify import get_ranges



log = logger(__file__)

# distribution_folder = config["settings"]["folders"]["distribution_sld"]

# TODO: move it from here (move it in config?)
default_obj = {

   # oltre alla scala quantistics servirebbe qualcosa qualitativa (i.e. [{"1"; "bad"}]

    "intervals": 5,
    "colorramp": "Reds",
    "colortype": None, #Sequential, Diverging, Qualitative
    "colors": None, #["#00000", "#111111"]
    "reverse": False, #["#00000", "#111111"]
    "ranges": None, #[0, 1, 2]
    "labels": None, #["label1", "label2"]
    "nodata": { # da vedere bene!
        "codes": None,
        "label": "No Data Value",
        "position": "on top"
    },
    "classificationtype": "jenks_caspall_forced",
    "joincolumn": None,
    "joindata": None, # or join_data?
    "doublecounting": False,
    "decimalvalues": 2,
    "jointype": "shaded"
}


class MapClassify():

    config = None

    def __init__(self, config):
        self.config = config

    def classify(self, data, distribution_url=None, distribution_folder=None):
        data = dict_merge(default_obj, data)

        # Get Ranges
        ranges = get_ranges(data)
        log.info("Ranges: " + str(ranges))
        data["intervals"] = len(ranges)
        log.info("Intervals: " + str(data["intervals"]))

        # Get Colors
        # # TODO: get colors based on real generated intervals
        colors = get_colors(data, data["intervals"])
        log.info("Colors: " + str(colors))

        # check if create shaded or point data
        if data["jointype"] == "shaded":
            return self.classify_sld(data, ranges, colors, distribution_url, distribution_folder)
        elif data["jointype"] == "point":
            # TODO: move it from here (and maybe also move it from sld creation (so it won't create a file)
            sld, legend = create_sld_xml(data, ranges, colors)
            return {"legend": legend}
        else:
            raise Exception('Classification "type":"' + data["jointype"] + '" not supported.')

    def classify_sld(self, data, ranges, colors, distribution_url=None, distribution_folder=None):
        distribution_folder = get_distribution_folder(self.config, distribution_folder)
        # create SLD with legend
        sld, legend = create_sld_xml(data, ranges, colors)

        # create file
        path, filename = _create_sld(distribution_folder, sld)

        # URL to the resource
        if distribution_url is None:
            return path
        else:
            url = distribution_url + filename
        return {"url": url, "legend": legend}

def _create_sld(distribution_folder, sld, extension=".sld"):
    # get the distribution folder
    filename = "sld_" + str(uuid.uuid4()) + extension
    path = os.path.join(distribution_folder, filename)
    with open(path, "w") as f:
        f.write(sld)
    return path, filename


def get_distribution_folder(config, distribution_folder=None):
    try:
        if distribution_folder is None:
            # turning relative to absolute path if required
            if not os.path.isabs(config["settings"]["folders"]["distribution_sld"]):
                # raster_path = os.path.normpath(os.path.join(os.path.dirname(__file__), self.config["settings"]["folders"]["distribution"]))
                # TODO ABS PATH (right?)
                config["settings"]["folders"]["distribution_sld"] = os.path.abspath(config["settings"]["folders"]["distribution_sld"])
            distribution_folder = config["settings"]["folders"]["distribution_sld"]
        if not os.path.isdir(distribution_folder):
            os.makedirs(distribution_folder)
    except Exception, e:
        log.error(e)
        raise Exception(e)
    return distribution_folder

