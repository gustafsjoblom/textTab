#
# -*- coding: utf-8 -*-#

# Copyright (C) 2016 haydent <www.httech.com.au>
#
# Basic plugin template created by:
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
# Copyright (C) 2009 Damien Churchill <damoxc@gmail.com>
# Copyright (C) 2010 Pedro Algarvio <pedro@algarvio.me>
#
# This file is part of textTab and is licensed under GNU General Public License 3.0, or later, with
# the additional special exception to link portions of this program with the OpenSSL library.
# See LICENSE for more details.
#

import gtk
import logging

from deluge.ui.client import client
from deluge.plugins.pluginbase import GtkPluginBase
import deluge.component as component
import deluge.common
from twisted.internet.task import LoopingCall
from deluge.ui.gtkui.torrentdetails import Tab
from common import get_resource

log = logging.getLogger(__name__)

class GtkUI(GtkPluginBase):
    def enable(self):
        self.glade = gtk.glade.XML(get_resource("config.glade"))

        component.get("Preferences").add_page("textTab", self.glade.get_widget("prefs_box"))
        component.get("PluginManager").register_hook("on_apply_prefs", self.on_apply_prefs)
        component.get("PluginManager").register_hook("on_show_prefs", self.on_show_prefs)
        
        self._text_tab = TextTab()
        #self._text_tab2 = TextTab()
        component.get("TorrentDetails").add_tab(self._text_tab)
        
        component.get("TorrentDetails").regenerate_positions()
        #component.get("TorrentDetails").add_tab(self._text_tab2)

        self.textTab_timer = LoopingCall(self._text_tab.update_tab)
        self.textTab_timer.start(5)

    def disable(self):
        component.get("Preferences").remove_page("textTab")
        component.get("TorrentDetails").remove_tab("TextTab")
        component.get("PluginManager").deregister_hook("on_apply_prefs", self.on_apply_prefs)
        component.get("PluginManager").deregister_hook("on_show_prefs", self.on_show_prefs)
        self.textTab_timer.stop()

    def on_apply_prefs(self):
        log.debug("applying prefs for textTab")
        config = {
            "path1":self.glade.get_widget("txt_path1").get_text()
        }
        client.texttab.set_config(config)

    def on_show_prefs(self):
        client.texttab.get_config().addCallback(self.cb_get_config)

    def cb_get_config(self, config):
        "callback for on show_prefs"
        self.glade.get_widget("txt_path1").set_text(config["path1"])


class TextTab(Tab):
    def __init__(self):
        Tab.__init__(self)
        glade_tab = gtk.glade.XML(get_resource("text_tab.glade"))

        self._name = "TextTab"
        self._child_widget = glade_tab.get_widget("text_tab")
        self._tab_label = glade_tab.get_widget("text_tab_label")

        self.textview = glade_tab.get_widget("text_tab_textview") 
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)

    def update_tab(self):
        client.texttab.get_text().addCallback(self.cb_get_text)
        
    def cb_get_text(self, text):        
        if text:
            log.info("textTab, file contents: \n%s" % text)
            self.textview.get_buffer().set_text(text) # would be better to only request and add new lines maybe rather than all

        else:
            log.info("textTab, file not found or empty")
            self.textview.get_buffer().set_text("file not found or empty")

    def __dest(self, widget, response):        
        widget.destroy()


    def update(self):
        pass
