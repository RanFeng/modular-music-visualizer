"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Quick FFplay wrapper if needed, listens to inputs from the stdin

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

from mmv.common.cmn_constants import LOG_NEXT_DEPTH, LOG_NO_DEPTH
import mmv.common.cmn_any_logger
from PIL import Image
import numpy as np
import subprocess
import logging
import copy
import time
import sys
import cv2


class FFplayWrapper:
    def configure(self, 
        ffplay_binary_path: str,  # Path to the FFplay binary
        width: int,
        height: int,
        pix_fmt: str,  # rgba, rgb24, bgra
        framerate: int,
        vflip = False,
        depth = LOG_NO_DEPTH,
    ) -> None:

        debug_prefix = "[FFplayWrapper.configure_pipe_images_to_video]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Add the rest of the command
        self.command = [
            ffplay_binary_path,
            "-pixel_format", pix_fmt,
            "-framerate", f"{framerate}",
            "-video_size", f"{width}x{height}",
            "-f", "rawvideo",
            "-i", "-"
        ]

        if vflip:
            self.command += ["-vf", "vflip"]

        # Log the command for generating final video
        logging.info(f"{depth}{debug_prefix} FFplay command is: {self.command}")
      
    def pipe_images_to_video(self):
        pass
    
    def start(self, stdin = subprocess.PIPE, stdout = subprocess.PIPE, depth = LOG_NO_DEPTH):
        debug_prefix = "[FFplayWrapper.start]"
        ndepth = depth + LOG_NEXT_DEPTH

        logging.info(f"{depth}{debug_prefix} Starting FFplay pipe subprocess with command {self.command}")

        # Create a subprocess in the background
        self.subprocess = subprocess.Popen(
            self.command,
            stdin  = stdin,
            stdout = stdout,
        )

        print(debug_prefix, "Open one time pipe")

        self.stop_piping = False
        self.lock_writing = False
        self.images_to_pipe = {}
