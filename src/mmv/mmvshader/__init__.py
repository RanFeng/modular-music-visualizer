"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Interface for MMVShader functionality

===============================================================================

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.

===============================================================================
"""

from mmv.common.cmn_constants import LOG_NEXT_DEPTH, PACKAGE_DEPTH, LOG_NO_DEPTH, LOG_SEPARATOR, STEP_SEPARATOR
import sys
import os

# Main wrapper class for the end user, facilitates MMV in a whole
class MMVShaderInterface:

    def __init__(self, interface, depth = LOG_NO_DEPTH, **kwargs):
        debug_prefix = "[MMVShaderInterface.__init__]"
        ndepth = depth + LOG_NEXT_DEPTH
        self.interface = interface
        self.prelude = self.interface.prelude

        # Where this file is located, please refer using this on the whole package
        # Refer to it as self.mmv_main.ROOT at any depth in the code
        # This deals with the case we used pyinstaller and it'll get the executable path instead
        if getattr(sys, 'frozen', True):    
            self.ROOT = os.path.dirname(os.path.abspath(__file__))
            print(f"{depth}{debug_prefix} Running directly from source code")
            print(f"{depth}{debug_prefix} Modular Music Visualizer Python package [__init__.py] located at [{self.ROOT}]")
        else:
            self.ROOT = os.path.dirname(os.path.abspath(sys.executable))
            print(f"{depth}{debug_prefix} Running from release (sys.executable..?)")
            print(f"{depth}{debug_prefix} Modular Music Visualizer executable located at [{self.ROOT}]")

        # # # Create MMV classes and stuff
