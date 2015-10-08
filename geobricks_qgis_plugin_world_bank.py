# -*- coding: utf-8 -*-
import os
import re
import urllib2
import simplejson
from shutil import copyfile
import fiona
from fiona.crs import from_epsg
from shapely.geometry import mapping, shape
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
from qgis.core import QgsStyleV2, QgsVectorGradientColorRampV2, QgsVectorLayer, QgsMapLayerRegistry, QgsGraduatedSymbolRendererV2, QgsSymbolV2,  QgsRendererRangeV2

# from geobricks_mapclassify.core.mapclassify import MapClassify



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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
from PyQt4.QtGui import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from geobricks_qgis_plugin_world_bank_dialog import GeobricksQgisPluginWorldBankDialog
import os.path


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


    def run(self):
        # TODO: how to style as default the map?

        # req = urllib2.Request('http://fenixapps2.fao.org/api/v1.0/en/codes/areagroup/qc')
        # response = urllib2.urlopen(req)
        # json = response.read()
        # data = simplejson.loads(json)
        #
        # values = []
        # for d in data['data']:
        #      values.append(d['label'])
        #
        # self.dlg.cbCountries.addItems(values)

        req = urllib2.Request('http://api.worldbank.org/indicators?per_page=500&format=json')

        response = urllib2.urlopen(req)
        json = response.read()
        data = simplejson.loads(json)

        # TODO cache codes
        values = []
        indicators = {}
        for d in data[1]:
            indicators[d['name']] = d['id']
            values.append(d['name'])

        self.dlg.cbIndicator.addItems(values)

        values = []
        for year in range(2012, 1980, -1):
            values.append(str(year))

        self.dlg.cbFromYear.addItems(values)
        self.dlg.cbToYear.addItems(values)



        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            print "Processing layers"

            indicator_name = self.dlg.cbIndicator.currentText()
            indicator = indicators[indicator_name]
            #print indicator

            fromYear = int(self.dlg.cbFromYear.currentText())-1
            toYear = int(self.dlg.cbToYear.currentText())
            print toYear, fromYear

            for year in range(toYear, fromYear, -1):
                year = str(year)
                print year

                #req = urllib2.Request('http://api.worldbank.org/countries/indicators/1.0.HCount.1.25usd?per_page=100&date=2008:2008&format=json')
                #req = urllib2.Request('http://api.worldbank.org/countries/indicators/NY.GDP.MKTP.CD?date=2013&format=json&per_page=10000')
                #req = urllib2.Request('http://api.worldbank.org/countries/indicators/AG.LND.ARBL.ZS?date=2012&format=json&per_page=10000')
                try:
                    request = 'http://api.worldbank.org/countries/all/indicators/' + indicator + '?date=' + year + '&format=json&per_page=10000'
                    print"Request: ", request

                    req = urllib2.Request(request)
                    response = urllib2.urlopen(req)
                    json = response.read()
                    data = simplejson.loads(json)
                    print "Request End"

                    # print data
                    clean_layer_name = re.sub('\W+','_', indicator_name) + "_" + year

                    output_base_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "output")
                    if not os.path.exists(output_base_path):
                        os.mkdir(output_base_path)

                    output_file = os.path.join(output_base_path, clean_layer_name + ".shp")
                    input_base_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")

                    # Read the original Shapefile
                    print "Writing: " + output_file
                    with fiona.collection(os.path.join(input_base_path, "baselayer_3857.shp"), 'r') as input:
                        # The output has the same schema
                        schema = input.schema.copy()
                        schema['properties']['value'] = 'float'

                        # write a new shapefile
                        # TODO: dinamic projection
                        with fiona.collection(output_file, 'w', crs=from_epsg(3857), driver='ESRI Shapefile', schema=schema) as output:
                            for elem in input:
                                for d in data[1]:
                                    code = d['country']['id']
                                    value = d['value']
                                    #print code, value
                                    # print elem['properties']
                                    #print elem['properties']['ISO2']
                                    if code == elem['properties']['ISO2']:
                                        # print value
                                        if value:
                                            elem['properties']['value'] = value
                                            output.write({'properties': elem['properties'],'geometry': mapping(shape(elem['geometry']))})

                    try:

                        # TODO: fix with fiona
                        copyfile(os.path.join(input_base_path, 'baselayer_3857.prj'), os.path.join(output_base_path, clean_layer_name + ".prj"))

                        print "Adding: " + indicator_name + ' (' + year +')'
                        layer = self.iface.addVectorLayer(
                            output_file,
                            indicator_name + ' (' + year +')',
                            "ogr")


                        print "Start creating style"
                        # TODO: calculate ranges
                        # define ranges: label, lower value, upper value, color name
                        # coffee_prices = (
                        #     ('Free', 0.0, 0.0, 'green'),
                        #     ('Cheap', 0.0, 1.5, 'yellow'),
                        #     ('Average', 1.5, 2.5, 'orange'),
                        #     ('Expensive', 2.5, 999.0, 'red'),
                        # )

                        # # create a category for each item in animals
                        # ranges = []
                        # for label, lower, upper, color in coffee_prices:
                        #     symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
                        #     symbol.setColor(QColor(color))
                        #     rng = QgsRendererRangeV2(lower, upper, symbol, label)
                        #     ranges.append(rng)

                        # # create the renderer and assign it to a layer
                        # expression = 'value' # field name
                        # renderer = QgsGraduatedSymbolRendererV2(expression, ranges)
                        # layer.setRendererV2(renderer)

                        # myTargetField = 'Value'
                        # myRangeList = []
                        # myOpacity = 1
                        # # Make our first symbol and range...
                        # myMin = 0.0
                        # myMax = 50.0
                        # myLabel = 'Group 1'
                        # myColour = QColor('#ffee00')
                        # mySymbol1 = QgsSymbolV2.defaultSymbol(layer.geometryType())
                        # mySymbol1.setColor(myColour)
                        # mySymbol1.setAlpha(myOpacity)
                        # myRange1 = QgsRendererRangeV2(myMin, myMax, mySymbol1, myLabel)
                        # myRangeList.append(myRange1)
                        # #now make another symbol and range...
                        # myMin = 50.1
                        # myMax = 100
                        # myLabel = 'Group 2'
                        # myColour = QColor('#00eeff')
                        # mySymbol2 = QgsSymbolV2.defaultSymbol(layer.geometryType())
                        # mySymbol2.setColor(myColour)
                        # mySymbol2.setAlpha(myOpacity)
                        # myRange2 = QgsRendererRangeV2(myMin, myMax, mySymbol2, myLabel)
                        # myRangeList.append(myRange2)
                        # myRenderer = QgsGraduatedSymbolRendererV2('', myRangeList)
                        # myRenderer.setMode(QgsGraduatedSymbolRendererV2.EqualInterval)
                        # myRenderer.setClassAttribute(myTargetField)
                        # layer.setRendererV2(myRenderer)

                        applyGraduatedSymbologyStandardMode(layer, 'Value', 5,  QgsGraduatedSymbolRendererV2.Jenks)

                        print "End creating style"
                    except Exception, e:
                        print e
                except Exception, e:
                    print e


def validatedDefaultSymbol( geometryType ):
    symbol = QgsSymbolV2.defaultSymbol( geometryType )
    if symbol is None:
        if geometryType == QGis.Point:
            symbol = QgsMarkerSymbolV2()
        elif geometryType == QGis.Line:
            symbol =  QgsLineSymbolV2 ()
        elif geometryType == QGis.Polygon:
            symbol = QgsFillSymbolV2 ()
    return symbol


def applyGraduatedSymbologyStandardMode( layer, field, classes, mode):
    # symbol = validatedDefaultSymbol( layer.geometryType() )
    # symbol = QgsFillSymbolV2()
    symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
    style = QgsStyleV2().defaultStyle()
    colorRamp = style.colorRampRef(u'Blues')
    print colorRamp
    #colorRamp = QgsVectorGradientColorRampV2.create({'color1':'255,0,0,255', 'color2':'0,0,255,255','stops':'0.25;255,255,0,255:0.50;0,255,0,255:0.75;0,255,255,255'})
    #print colorRamp
    renderer = QgsGraduatedSymbolRendererV2.createRenderer( layer, field, classes, mode, symbol, colorRamp )
    layer.setRendererV2( renderer )

