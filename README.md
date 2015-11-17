# ranger config
Contains ranger customized configuration, plugins and commands.

commands.py defines a filterby command see documentation at: https://github.com/moisesluza/ranger/blob/master/commands.py
plugin_linemode.py defines a new linemode to show file attributes in the file browser
rc.conf contains ranger standar configuration and configuration to enable linemode defined in plugin_linemode.py

Installing
----------

1. Install ranger (v.1.7.2 prefered) by following ranger installation instructions: https://github.com/hut/ranger
2. Copy all files to the following directories:
    * ~/.config/ranger/rc.conf
    * ~/.config/ranger/commands.py
    * ~/.config/ranger/plugins/plugin_linemode.py
3. Start ranger and play
