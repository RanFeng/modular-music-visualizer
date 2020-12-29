"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Wrapper for the Shady project https://github.com/polyfloyd/shady
so we can render Shadertoy syntax GLSLs to a video. Let the new era of MMV
begin!

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

from mmv.common.cmn_constants import LOG_NEXT_DEPTH, LOG_NO_DEPTH, STEP_SEPARATOR
import subprocess
import logging
import sys
import os


class MMVShaderShady:
    def __init__(self, mmv_shader_main, depth = LOG_NO_DEPTH):
        debug_prefix = "[MMVShaderShady.__init__]"
        ndepth = depth + LOG_NEXT_DEPTH
        self.mmv_shader_main = mmv_shader_main