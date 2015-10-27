# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeobricksQgisPluginWorldBank
                                 A QGIS plugin
 Plugin for Qgis 2.x. Creates thematic maps with World Bank data. 
                              -------------------
        begin                : 2015-10-08
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Simone Murzilli/GeoBricks
        email                : simone.murzilli@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import glob
import re
import urllib2
import json
from shutil import copyfile

# TODO: check if all imports are needed
from qgis.core import QgsRendererRangeV2LabelFormat, QgsMessageLog, QgsFeature, QgsField, QgsStyleV2, QgsVectorGradientColorRampV2, QgsVectorLayer, QgsMapLayerRegistry, QgsGraduatedSymbolRendererV2, QgsSymbolV2,  QgsRendererRangeV2
from PyQt4.QtCore import *
from PyQt4 import QtCore
# from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QSizePolicy

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from geobricks_qgis_plugin_world_bank_dialog import GeobricksQgisPluginWorldBankDialog
import os.path

from PyQt4.QtGui import QProgressBar
from qgis.gui import QgsMessageBar


class GeobricksQgisPluginWorldBank:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GeobricksQgisPluginWorldBank_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = GeobricksQgisPluginWorldBankDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Geobricks Qgis Plugin WorldBank')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'GeobricksQgisPluginWorldBank')
        self.toolbar.setObjectName(u'GeobricksQgisPluginWorldBank')

        # TODO: check if there is a better way to handle inizialition
        self.initialized = False

        # ID used for the messagebar 
        self.QGSMESSAGEBAR_ID = 'GeobricksWorldBankPlugin'



    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GeobricksQgisPluginWorldBank', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/GeobricksQgisPluginWorldBank/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u''),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Geobricks Qgis Plugin WorldBank'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def process_layers(self):

        processed_layers = 0
        self.dlg.progressBar.setValue(processed_layers)
        self.dlg.progressText.setText('Fetching Data from the World Bank')

        indicator_name = self.dlg.cbIndicator.currentText()
        indicator = self.indicators[indicator_name]

        from_year = int(self.dlg.cbFromYear.currentText())
        to_year = int(self.dlg.cbToYear.currentText()) + 1
        total_years = from_year - to_year

        layers = []
        layers_not_available = []

        # create tmp layer
        tmp_layer = QgsVectorLayer("Polygon?crs=EPSG:4326", "tmp", "memory")
        tmp_data_provider = tmp_layer.dataProvider()

        # add fields
        tmp_data_provider.addAttributes([QgsField("value", QVariant.Double)])

        for year in range(from_year, to_year):
            year = str(year)
            layer_name = year + ' '+ indicator_name

            # QgsMessageLog('processing ' + layer_name) 
            QgsMessageLog.logMessage(layer_name, self.QGSMESSAGEBAR_ID, QgsMessageLog.INFO)
            self.dlg.progressText.setText('Processing: ' + layer_name)

            try:

                # Create Layer                
                layer, addedValue = create_layer(tmp_layer, indicator, indicator_name, year)

                # check if the layer has been changed
                if addedValue:                
                    layers.append(layer)
                else:
                    # TODO: give a message to the user. something like "data are not available for this year"
                    QgsMessageLog.logMessage("WARN: there are no data available for " + str(year), self.QGSMESSAGEBAR_ID, QgsMessageLog.WARNING)
                    layers_not_available.append(year)

            except Exception, e:
                layers_not_available.append(year)

            # changing progress bar value  
            processed_layers += 1
            self.dlg.progressBar.setValue(int((float(processed_layers)/float(total_years)) * 100))

        # commit changed on tmp layer
        tmp_layer.commitChanges()

        renderer = create_join_renderer(tmp_layer, 'value', 5,  QgsGraduatedSymbolRendererV2.Jenks)

        for index, l in enumerate(layers):
            l.setRendererV2(renderer)
            QgsMapLayerRegistry.instance().addMapLayer(l)
            self.iface.legendInterface().setLayerVisible(l, (index == len(layers)-1))

        self.iface.mapCanvas().refresh()

        self.dlg.progressText.setText('Process Finished')

        if len(layers_not_available) > 0:
            self.iface.messageBar().pushMessage(indicator_name, 'Data are not available for ' + ', '.join(layers_not_available) + '', level=QgsMessageBar.WARNING)

        self.dlg.close()

    def update_indicator(self):
        self.dlg.cbIndicator.clear()
        source_name = self.dlg.cbSource.currentText()
        source_id = self.sources[source_name]

        # get World Bank data indicators by source ID
        data = get_world_bank_indicators(source_id)

        # cache codes
        values = []
        self.indicators = {}
        for d in data:
            self.indicators[d['name']] = d['id']
            values.append(d['name'])

        values.sort()
        self.dlg.cbIndicator.addItems(values)

    def remove_tmp_path(self):
        # TODO: move to a function the remove the old files in output folder
        if os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), "output")):
            files = glob.glob(os.path.join(os.path.dirname(os.path.realpath(__file__)), "output", "*"))
            for f in files:
                os.remove(f)

    def initialize_sources(self):
        # TODO: load sources dinamically
        data = [
            {
                'name': 'Doing Business',
                'id': '1'
            },
            {
                'name': 'World Development Indicators',
                'id': '2'
            },
            {
                'name': 'Worldwide Governance Indicators',
                'id': '3'
            },
            {
                'name': 'Subnational Malnutrition Database',
                'id': '5'
            },
            {
                'name': 'International Debt Statistics',
                'id': '6'
            }
        ]

        values = []
        self.sources = {}
        for d in data:
            self.sources[d['name']] = d['id']
            values.append(d['name'])

        self.dlg.cbSource.addItems(values)

    def initialize_years(self):
        # TODO: load the years dinamically
        values = []
        for year in range(2014, 1980, -1):
            values.append(str(year))

        self.dlg.cbFromYear.addItems(values)
        self.dlg.cbToYear.addItems(values)

    def run(self):

        # if the interface is initiated
        if self.initialized:
            self.dlg.progressText.setText('')
            self.dlg.progressBar.setValue(0)

        if not self.initialized:
            # dirty check if interface was already initialized
            self.initialized = True

            self.remove_tmp_path()

            # initialize selectors
            self.initialize_sources()
            self.initialize_years()

            # call first indicator
            self.update_indicator()
            self.dlg.cbSource.currentIndexChanged.connect(self.update_indicator)

            # on OK and Cancel click
            self.dlg.buttonBox.accepted.connect(self.process_layers)
            self.dlg.buttonBox.rejected.connect(self.dlg.close)

        # show the dialog
        self.dlg.show()


def create_layer(tmp_layer, indicator, indicator_name, year):

    tmp_data_provider = tmp_layer.dataProvider()
    tmp_layer.startEditing()
    tmp_feature = QgsFeature()

    # get world bank data
    data = get_world_bank_data(indicator, year)

    # getting layer_name
    layer_name = indicator_name + " (" + year + ")"
    clean_layer_name = re.sub('\W+','_', indicator_name) + "_" + year

    # creating output path
    output_base_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "output")
    if not os.path.exists(output_base_path):
        os.mkdir(output_base_path)

    # retrieving input shp
    output_file = os.path.join(output_base_path, clean_layer_name + ".shp")
    input_base_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")

    # copy resource file to output
    # resource_files = glob.glob(os.path.join(input_base_path, "ne_110m_admin_0_*"))
    resource_files = glob.glob(os.path.join(input_base_path, "ne_110m_admin_0_*"))
    for resource_file in resource_files:
        base, extension = os.path.splitext(resource_file)
        copyfile(resource_file, os.path.join(output_base_path, clean_layer_name + extension))

    # Editing output_file
    layer = QgsVectorLayer(output_file, layer_name, "ogr")
    layer.startEditing()

    # TODO: add data check instead of the addedValue boolean?
    addedValue = False
    for feat in layer.getFeatures():
        if feat['iso_a2'] is not None:
            for d in data[1]:
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


def get_world_bank_data(indicator, year):
    request = 'http://api.worldbank.org/countries/all/indicators/' + indicator + '?date=' + year + '&format=json&per_page=10000'
    req = urllib2.Request(request)
    response = urllib2.urlopen(req)
    json_data = response.read()
    if json_data:
        return json.loads(json_data)
    else:
        return None


def get_world_bank_indicators(source_id):
    req = urllib2.Request('http://api.worldbank.org/source/' + str(source_id) + '/indicators?per_page=1500&format=json')
    response = urllib2.urlopen(req)
    json_data = response.read()
    return json.loads(json_data)[1]

