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

        # Log action
        logging.info(f"{depth}{debug_prefix} Initialized MMVShaderShady, starting up empty configuration")

        # Reset to a blank config
        self.reset(depth = ndepth)
        self.HAVE_FFMPEG_WRAPPER = False

    # Get one Common FFmpegWrapper class, needed!!
    def get_ffmpeg_wrapper(self, ffmpeg, depth = LOG_NO_DEPTH):
        debug_prefix = "[MMVShaderShady.reset]"
        ndepth = depth + LOG_NEXT_DEPTH
        self.HAVE_FFMPEG_WRAPPER = True

        # Log action
        logging.info(f"{depth}{debug_prefix} Get FFmpeg wrapper located at [{ffmpeg}]")

        self.ffmpeg = ffmpeg

    # Reset to a blank configuration
    def reset(self, depth = LOG_NO_DEPTH):
        debug_prefix = "[MMVShaderShady.reset]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        logging.info(f"{depth}{debug_prefix} Reset config")

        # Command to execute shady
        self.__command = []
    
    """
    kwargs:
        shady_binary,
        width, height, framerate,
        main_glsl
    """
    def base_configuration(self, depth = LOG_NO_DEPTH, **kwargs):
        debug_prefix = "[MMVShaderShady.reset]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        logging.info(f"{depth}{debug_prefix} Reset config")

        self.__command += [
            kwargs.get("shady_binary"),
            "-i", kwargs.get("main_glsl"),
            "-ofmt", "rgba32",
            "-g", str(kwargs.get("width")) + "x" + str(kwargs.get("height")),
            "-f", str(kwargs.get("framerate"))
        ]

        logging.info(f"{depth}{debug_prefix} Shady partial run command is: {self.__command}")

    # Execute
    def render_to_video(self, depth = LOG_NO_DEPTH):
        debug_prefix = "[MMVShaderShady.render_to_video]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        logging.info(f"{depth}{debug_prefix} Rendering to video")

        # If we haven't set up ffmpeg wrapper or input is not accepting from piper, error
        if (not self.HAVE_FFMPEG_WRAPPER) or (not "-i -" in ' '.join(self.ffmpeg.ffmpeg_command)):
            logging.critical(f"{depth}{debug_prefix} Please send an FFmpegWrapper on the function get_ffmpeg_wrapper with input_video_source=\"pipe\"")
            sys.exit(-1)

        # Start FFmpeg pipe
        self.ffmpeg.pipe_images_to_video()

        # Warn command
        logging.info(f"{depth}{debug_prefix} Running pipe to video shady command: {self.__command}, redirect stdout to FFmpeg pipe stding")

        # Create the shady subprocess, redirect its output to the FFmpeg's pipe stdin
        self.shady_subprocess = subprocess.run(
            self.__command,
            stdout = self.ffmpeg.pipe_subprocess.stdin,
            # stdout = subprocess.PIPE,
        )
