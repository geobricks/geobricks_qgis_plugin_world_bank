import os
import re
import glob
from shutil import copyfile
from qgis.core import QgsRendererRangeV2LabelFormat, QgsFeature, QgsStyleV2, QgsVectorLayer, QgsGraduatedSymbolRendererV2, QgsSymbolV2


def create_layer(download_path, tmp_layer, indicator, indicator_name, data, year):

    tmp_data_provider = tmp_layer.dataProvider()
    tmp_layer.startEditing()
    tmp_feature = QgsFeature()

    # get world bank data
    # data = get_world_bank_data(indicator, year)

    # getting layer_name
    layer_name = indicator_name + " (" + year + ")"
    clean_layer_name = re.sub('\W+', '_', indicator_name) + "_" + year

    # creating output path
    # output_base_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "output")
    # if not os.path.exists(output_base_path):
    #     os.mkdir(output_base_path)

    # retrieving input shp
    # output_file = os.path.join(output_base_path, clean_layer_name + ".shp")
    output_file = os.path.join(download_path, clean_layer_name + ".shp")
    input_base_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")

    # copy resource file to output
    # resource_files = glob.glob(os.path.join(input_base_path, "ne_110m_admin_0_*"))
    resource_files = glob.glob(os.path.join(input_base_path, "ne_110m_admin_0_*"))
    for resource_file in resource_files:
        base, extension = os.path.splitext(resource_file)
        copyfile(resource_file, os.path.join(download_path, clean_layer_name + extension))

    # Editing output_file
    layer = QgsVectorLayer(output_file, layer_name, "ogr")
    layer.startEditing()

    # TODO: add data check instead of the addedValue boolean?
    addedValue = False
    for feat in layer.getFeatures():
        if feat['iso_a2'] is not None:
            for d in data:
                code = d['country']['id']
                value = d['value']
                if code == feat['iso_a2']:
                    if value:
                        # TODO: automatize the index 5 of feat['iso_a2']
                        layer.changeAttributeValue(feat.id(), 5, float(value))
                        tmp_feature.setAttributes([float(value)])
                        # TODO add all togheter
                        tmp_data_provider.addFeatures([tmp_feature])
                        addedValue = True
                        break

    layer.commitChanges()
    return layer, addedValue


def create_join_renderer(layer, field, classes, mode, color='Blues'):
    symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
    style = QgsStyleV2().defaultStyle()
    colorRamp = style.colorRampRef(color)
    renderer = QgsGraduatedSymbolRendererV2.createRenderer(layer, field, classes, mode, symbol, colorRamp)
    label_format = create_join_label_format(2)
    renderer.setLabelFormat(label_format)
    return renderer


def create_join_label_format(precision):
    format = QgsRendererRangeV2LabelFormat()
    template="%1 - %2 metres"
    format.setFormat(template)
    format.setPrecision(precision)
    format.setTrimTrailingZeroes(True)
    return format
