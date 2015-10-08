import numpy
from pysal.esda import mapclassify


def get_ranges(data):
    # custom ranges
    if "ranges" in data and data["ranges"] is not None:
        # adding another fake range step to the array
        data["ranges"].append(data["ranges"][len(data["ranges"])-1])
        return data["ranges"]

    # else classification
    else:
        return classify_values(get_data_values(data), data["intervals"], data["classificationtype"])


def get_data_values(data):
    data_values = []
    # return None if "data" not in data else data["data"]
    for d in data["joindata"]:
        for key in d:
            if isinstance(d[key], basestring):
                d[key] = float(d[key])
            data_values.append(d[key])

    # print data_values
    # TODO: use unique values? list(set(data_values)) or having double counting values? i.e. in quantile it counts.
    if "doublecounting" in data and data["doublecounting"]:
        return data_values
    else:
        return list(set(data_values))


def classify_values(values, intervals, classification_type):
    intervals = intervals if intervals <= len(values) else len(values)
    values = numpy.array(values)
    classification_type = classification_type.lower()

    if classification_type == "jenks_caspall":
        return classify_jenks_caspall(values, intervals)
    elif classification_type == "jenks_caspall_forced":
        return classify_jenks_caspall_forced(values, intervals)
    elif classification_type == "natural_breaks":
        return classify_natural_breaks(values, intervals)
    elif classification_type == "quantile":
        return classify_quantile(values, intervals)
    elif classification_type == "equal_interval":
        return classify_equal_interval(values, intervals)
    elif classification_type == "percentiles":
        return classify_percentiles(values)


def classify_jenks_caspall(values, intervals):
    result = mapclassify.Jenks_Caspall(values, intervals)
    return result.bins


def classify_jenks_caspall_forced(values, intervals):
    result = mapclassify.Jenks_Caspall_Forced(values, intervals)
    return result.bins


def classify_natural_breaks(values, intervals):
    result = mapclassify.natural_breaks(values, intervals)
    # print result.bins
    return result


def classify_quantile(values, intervals):
    result = mapclassify.quantile(values, intervals)
    return result


def classify_percentiles(values):
    result = mapclassify.Percentiles(values)
    return result.bins


def classify_equal_interval(values, intervals):
    result = mapclassify.Equal_Interval(values, intervals)
    return result.bins

