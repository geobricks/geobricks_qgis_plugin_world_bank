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
from qgis.core import QgsStyleV2, QgsVectorGradientColorRampV2, QgsVectorLayer, QgsMapLayerRegistry, QgsGraduatedSymbolRendererV2, QgsSymbolV2,  QgsRendererRangeV2
from PyQt4 import QtCore
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon

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

        # TODO: check if there is a better way to handle inizialition
        self.initialized = False

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
        print "PROCESSING LAYERS..."

        processed_layers = 0
        self.dlg.progressBar.setValue(processed_layers)
        self.dlg.progressText.setText('Fetching Data from the World Bank')

        indicator_name = self.dlg.cbIndicator.currentText()
        indicator = self.indicators[indicator_name]
        #print indicator

        fromYear = int(self.dlg.cbFromYear.currentText())
        toYear = int(self.dlg.cbToYear.currentText()) + 1
        print toYear, fromYear

        total = toYear - fromYear

        print total

        layers = []

        for year in range(fromYear, toYear):
            year = str(year)
            print year
            self.dlg.progressText.setText('Processing: ' + year + ' '+ indicator_name)


            #req = urllib2.Request('http://api.worldbank.org/countries/indicators/1.0.HCount.1.25usd?per_page=100&date=2008:2008&format=json')
            #req = urllib2.Request('http://api.worldbank.org/countries/indicators/NY.GDP.MKTP.CD?date=2013&format=json&per_page=10000')
            #req = urllib2.Request('http://api.worldbank.org/countries/indicators/AG.LND.ARBL.ZS?date=2012&format=json&per_page=10000')
            try:
                request = 'http://api.worldbank.org/countries/all/indicators/' + indicator + '?date=' + year + '&format=json&per_page=10000'
                # print"Request: ", request

                req = urllib2.Request(request)
                response = urllib2.urlopen(req)
                json_data = response.read()
                data = json.loads(json_data)
                # print "Request End"

                # print data
                clean_layer_name = re.sub('\W+','_', indicator_name) + "_" + year


                # creating output path
                output_base_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "output")
                if not os.path.exists(output_base_path):
                    os.mkdir(output_base_path)

                # retrieving input shp
                output_file = os.path.join(output_base_path, clean_layer_name + ".shp")
                input_base_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")

                #copy resource file to output
                resource_files = glob.glob(os.path.join(input_base_path, "ne_110m_admin_0_*"))
                for resource_file in resource_files:
                    base, extension = os.path.splitext(resource_file)                      
                    copyfile(resource_file, os.path.join(output_base_path, clean_layer_name + extension))


                # Editing output_file
                print "Editing: " + output_file
                layer = QgsVectorLayer(output_file, clean_layer_name, "ogr")
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
                                    # print feat['iso_a2'], value
                                    # TODO: automatize the index 63 of feat['iso_a2']
                                    layer.changeAttributeValue(feat.id(), 63 , float(value))
                                    addedValue = True
                                    break
                                    # (UpdateFeatureID,FieldToUpdate,self.CurrentWidget.text(),True)             
                                    # layer.changeAttributeValue(feat.id(), 2, 30)

                layer.commitChanges()
                
                # check if the layer has been changed
                if addedValue:                
                    layers.append(layer)
                else:
                    # TODO: give a message to the user. something like "data are not available for this year"
                    print "WARN: there are no data available for" + str(year)
                    print data 


                processed_layers = processed_layers+1
                self.dlg.progressBar.setValue(int((float(processed_layers)/float(total)) *100))

                # print "End creating style"
            except Exception, e:
                print e

        print layers
        print len(layers)
        for l in layers:
            QgsMapLayerRegistry.instance().addMapLayer(l)

            applyGraduatedSymbologyStandardMode(l, 'value', 5,  QgsGraduatedSymbolRendererV2.Jenks)
        self.dlg.progressText.setText('Process Finished')



    def run(self):

        if not self.initialized:

            # dirty check if interface was already initialized            
            self.initialized = True

            # req = urllib2.Request('http://api.worldbank.org/indicators?per_page=500&format=json')
            # response = urllib2.urlopen(req)
            # json = response.read()
            # data = simplejson.loads(json)
            # # TODO cache codes
            # values = []
            # self.indicators = {}
            # for d in data[1]:
            #     self.indicators[d['name']] = d['id']
            #     values.append(d['name'])

            # self.dlg.cbIndicator.addItems(values)

            data = [
            {
                'name': 'GPS (current US$)',
                'id': 'NY.GDP.MKTP.CD'
            },
            {
                'name': 'Rural Population',
                'id': 'SP.RUR.TOTL'
            },
            {
                'name': 'Forest area (% of land area)',
                'id': 'AG.LND.FRST.ZS'
            },
            ]

            values = []
            self.indicators = {}
            for d in data:
                self.indicators[d['name']] = d['id']
                values.append(d['name'])

            self.dlg.cbIndicator.addItems(values)

            # TODO: load the years dinamically
            values = []
            for year in range(2014, 1980, -1):
                values.append(str(year))

            self.dlg.cbFromYear.addItems(values)
            self.dlg.cbToYear.addItems(values)

            QtCore.QObject.connect(self.dlg.createLayers, QtCore.SIGNAL("clicked()"), self.process_layers)



        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass


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
    # print colorRamp
    #colorRamp = QgsVectorGradientColorRampV2.create({'color1':'255,0,0,255', 'color2':'0,0,255,255','stops':'0.25;255,255,0,255:0.50;0,255,0,255:0.75;0,255,255,255'})
    #print colorRamp
    renderer = QgsGraduatedSymbolRendererV2.createRenderer(layer, field, classes, mode, symbol, colorRamp)
    layer.setRendererV2(renderer)

