# This is a plugin for Rhytmbox for seeking in current playing song.
# This plugin is dual-licensed under GPL and Apache License (see below).

# Copyright (C) 2010 Thomas Bartensud
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

# Copyright 2010 Thomas Bartensud
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import rb
import gtk

ui_str = """
<ui>
  <toolbar name="ToolBar">
    <placeholder name="PluginPlaceholder">
      <toolitem name="SeekBack" action="SeekBack"/>
      <toolitem name="SeekForward" action="SeekForward"/>
    </placeholder>
  </toolbar>
  <menubar name="MenuBar">
    <menu name="ControlMenu" action="Control">
      <menuitem name="SeekBack" action="SeekBack"/>
      <menuitem name="SeekForward" action="SeekForward"/>
    </menu>
  </menubar>
</ui>
"""


class Seek(rb.Plugin):

	def __init__(self):
		rb.Plugin.__init__(self)
		
	def load_icon(self, filename, name):
		icon_file_name = self.find_file(filename)
		print 'Icon found: %s' %(icon_file_name)
		iconsource = gtk.IconSource()
		iconsource.set_filename(icon_file_name)
		iconset = gtk.IconSet()
		iconset.add_source(iconsource)
		iconfactory = gtk.IconFactory()
		iconfactory.add(name, iconset)
		iconfactory.add_default()


	def activate(self, shell):
		self.seekTime = 10 # seek time in seconds. Adjust to your needs.

                # define buttons for seeking backward and forward
		self.load_icon('media-seek-backward.svg', 'rb-seek-back')
		self.actionBack= gtk.Action('SeekBack', _('Seek backward'),
					 _('Seek backward'),
					 'rb-seek-back')
		self.activate_id = self.actionBack.connect('activate', self.seek_back, shell)

                self.load_icon('media-seek-forward.svg', 'rb-seek-forward')
		self.actionForward = gtk.Action('SeekForward', _('Seek forward'),
					 _('Seek forward'),
					 'rb-seek-forward')
		self.activate_idForward = self.actionForward.connect('activate', self.seek_forward, shell)

                self.enable_buttons(False)                

		self.action_group = gtk.ActionGroup('SeekPluginActions')
		self.action_group.add_action_with_accel(self.actionBack, '<Control>Left')
		self.action_group.add_action_with_accel(self.actionForward, '<Control>Right')
		
		uim = shell.get_ui_manager ()
		uim.insert_action_group(self.action_group, 0)
		self.ui_id = uim.add_ui_from_string(ui_str)
		uim.ensure_update()

                # init event listener
                self.evPlayingSongChanged_id = shell.get_player().connect('playing-song-changed', self.playing_song_changed)


	def seek(self, shell, seekTime):
                shellPlayer = shell.props.shell_player
		if shellPlayer.get_playing_entry(): # works also if song playing is paused
			newPlayingTime = shellPlayer.get_playing_time() + seekTime
			newPlayingTime = max(newPlayingTime, 0)
                        if newPlayingTime > shellPlayer.get_playing_song_duration():
                            shellPlayer.do_next()
                        else:
                            #print 'Seeking %d seconds in playing song to position: %d seconds' % (seekTime, newPlayingTime)
                            shellPlayer.set_playing_time(newPlayingTime)
                            # update ui (progress bar)
                            # shell.get_ui_manager().ensure_update() # has not effect; todo: find the correct UI update method.

	def seek_back(self, action, shell):
                self.seek(shell, -self.seekTime)

	def seek_forward(self, action, shell):
                self.seek(shell, self.seekTime)


        def enable_buttons(self, enabled):
                self.actionBack.set_sensitive(enabled)
                self.actionForward.set_sensitive(enabled)


	def playing_song_changed(self, player, entry):
		#print "playing song changed: %s" %(entry)
                if entry and player.props.player.seekable():
                    self.enable_buttons(True)
                else:
                    self.enable_buttons(False)


	def deactivate(self, shell):
		uim = shell.get_ui_manager()
		uim.remove_ui (self.ui_id)
		uim.remove_action_group (self.action_group)

		self.action_group = None
		self.actionBack= None
                self.actionForward = None
		del self.seekTime