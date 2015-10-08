from brewer2mpl import get_map as brewer2mpl_get_map
from geobricks_common.core.log import logger

log = logger(__file__)


def get_colors(data, intervals):
    reverse = False if "reverse" not in data else data["reverse"]
    intervals = 3 if intervals < 3 else intervals
    if "colors" in data and data["colors"] is not None:
        if reverse:
            return data["colors"][::-1]
        else:
            return data["colors"]
    else:
        color_ramp = data["colorramp"]
        # intervals = data["intervals"]
        try:
            return brewer2mpl_get_map(color_ramp, "Sequential", intervals, reverse=reverse).hex_colors
        except Exception, e:
            log.warn(e)
            pass
        try:
            return brewer2mpl_get_map(color_ramp, "Diverging", intervals, reverse=reverse).hex_colors
        except Exception, e:
            log.warn(e)
            pass
        try:
            return brewer2mpl_get_map(color_ramp, "Qualitative", intervals, reverse=reverse).hex_colors
        except Exception, e:
            log.warn(e)
            pass
    return None
