

def create_sld_xml(data, ranges, colors, labels=None):
    return create_quantitative_sld(data, ranges, colors, labels)


def create_quantitative_sld():
    return None


def create_quantitative_sld(data, ranges, colors, labels=None):
    rules = []
    values = data["joindata"]
    decimalvalues = data["decimalvalues"]
    join_column = data["joincolumn"] if "joincolumn" in data and data["joincolumn"] is not None else ""
    # TODO: if layers not set and "shaded" jointype should throw an error
    layers = data["layers"] if "layers" in data else ""

    for i in xrange(len(ranges)-1):
        range = round(ranges[i], decimalvalues)
        rules.append({
            "range": range,
            "color": colors[i],
            "label": "&lt;= " + str(range),
            "codes": []
        })

    # last rule is > than the last-1 value
    range = round(ranges[len(ranges)-2], decimalvalues)
    rules.append({
        "range": range,
        "color": colors[len(ranges)-1],
        "label": "&gt; " + str(range),
        "codes": []
    })

    for v in values:
        for key in v:
            added = False
            for rule in rules:
                if float(v[key]) <= float(rule["range"]):
                    rule["codes"].append(key)
                    added = True
                    break

            # add to the last rule is code not added previously
            if added is False:
                rules[len(rules)-1]["codes"].append(key)


    # crete sld
    sld = sld_open(layers)
    for i in xrange(len(rules)-1):
        # print rules[i]
        sld += sld_create_rule(str(rules[i]["label"]), join_column, rules[i]["codes"], rules[i]["color"])

    # last rule is > than the last-1 value
    # print rules[len(rules)-1]
    sld += sld_create_rule(str(rules[len(rules)-1]["label"]), join_column, rules[len(rules)-1]["codes"], rules[len(rules)-1]["color"])

    # close the sld
    sld += sld_close()
    # print sld
    return sld, rules


def sld_open(layers):
    sld = '<?xml version="1.0" encoding="UTF-8"?><sld:StyledLayerDescriptor xmlns:sld="http://www.opengis.net/sld" xmlns="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" version="1.0.0">'
    sld += '<sld:NamedLayer>'
    sld += '<sld:Name>' + layers + '</sld:Name>'
    sld += '<sld:UserStyle>'
    sld += '<sld:FeatureTypeStyle>'
    return sld


def sld_close():
    sld = '</sld:FeatureTypeStyle>'
    sld += '</sld:UserStyle>'
    sld += '</sld:NamedLayer>'
    sld += '</sld:StyledLayerDescriptor>'
    return sld


def sld_create_rule(title, join_column, codes, color, borders=None):
    sld = "<sld:Rule>"
    sld += sld_add_title(title)

    # add filters
    sld += sld_add_filter(join_column, codes)

    # add Polygon symbolizer
    sld += sld_add_polygonsymbolizer(color)
    sld += "</sld:Rule>"
    return sld


def sld_add_title(title):
    return "<sld:Title>" + str(title) + "</sld:Title>"


def sld_add_filter(join_column, codes):
    sld = "<ogc:Filter>"

    # TODO: fix it workaround for SLD
    if len(codes) == 0:
        sld += sld_add_property('PropertyIsEqualTo', join_column, "-9999999")

    if len(codes) > 1:
        sld += '<ogc:Or>'

    for code in codes:
        sld += sld_add_property('PropertyIsEqualTo', join_column, code)
        # sld += '<ogc:PropertyIsEqualTo>'
        # sld += '<ogc:PropertyName>' + join_column + '</ogc:PropertyName>'
        # sld += '<ogc:Literal>' + code + '</ogc:Literal>'
        # sld += '</ogc:PropertyIsEqualTo>'

    if len(codes) > 1:
        sld += '</ogc:Or>'
    sld += "</ogc:Filter>"
    return sld


def sld_add_property(property, join_column, value):
    sld = '<ogc:' + property + '>'
    sld += '<ogc:PropertyName>' + join_column + '</ogc:PropertyName>'
    sld += '<ogc:Literal>' + value + '</ogc:Literal>'
    sld += '</ogc:' + property + '>'
    return sld


def sld_add_polygonsymbolizer(color):
    sld = '<sld:PolygonSymbolizer>'
    sld += '<sld:Fill>'
    sld += '<sld:CssParameter name="fill">' + color + '</sld:CssParameter>'
    sld += '</sld:Fill>'
    sld += '</sld:PolygonSymbolizer>'
    return sld
