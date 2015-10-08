# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeobricksQgisPluginWorldBank
                                 A QGIS plugin
 Plugin for Qgis 2.x. Creates thematic maps with World Bank data. 
                             -------------------
        begin                : 2015-10-08
        copyright            : (C) 2015 by Simone Murzilli/GeoBricks
        email                : simone.murzilli@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load GeobricksQgisPluginWorldBank class from file GeobricksQgisPluginWorldBank.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .geobricks_qgis_plugin_world_bank import GeobricksQgisPluginWorldBank
    return GeobricksQgisPluginWorldBank(iface)
