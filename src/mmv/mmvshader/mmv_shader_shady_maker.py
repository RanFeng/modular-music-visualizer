"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Make shader layers for Shady to render

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
import mmv.common.cmn_any_logger
from PIL import Image
import numpy as np
import logging
import sys
import os


class MMVShaderShadyMaker:
    def __init__(self, mmv_shader_main):
        debug_prefix = "[MMVShaderShadyMaker.__init__]"
        self.mmv_shader_main = mmv_shader_main
        self.indent = "    "
        self.n = None
    
    # Get the empty shader, add the mmv-specifications.glsl file
    def empty_shader(self, shader_type):
        self.shader_type = shader_type
        sep = os.path.sep
        with open(f"{self.mmv_shader_main.interface.SHADERS_LOCATED_AT}{sep}shady{sep}empty_{shader_type}_shader.glsl", "r") as f:
            self.shader = f.read()
        self.include_shader(f"{self.mmv_shader_main.interface.SHADERS_LOCATED_AT}{sep}shady{sep}mmv_specification.glsl")
    
    # DEBUG, show what is being written
    def shader_replace(self, old, new):
        debug_prefix = "[MMVShaderShadyMaker.add_mapping]"

        # Debug what we're changing
        logging.info(f"{debug_prefix} Replacing on the shader")
        logging.info(f"{debug_prefix} [OLD] {old}")
        logging.info(f"{debug_prefix} [NEW] {new}")

        # Replace on the shader
        self.shader = self.shader.replace(old, new)
    
    # DEBUG Write the current shader to the runtime directory
    def save(self):
        runtime = self.mmv_shader_main.context.directories.runtime
        if self.n is None:
            self.n = len(os.listdir(runtime))
        save_path = f"{runtime}{os.path.sep}{self.shader_type}_{self.n}_{self.mmv_shader_main.utils.get_unique_id(silent = True)}.glsl"
        with open(save_path, "w") as f:
            f.write(self.shader)
        self.path = save_path

    # Add #pragma use "path" to the mappings on a shader (usually importing MMV specifications)
    def include_shader(self, path):
        debug_prefix = "[MMVShaderShadyMaker.include_shader]"

        # Path doesn't exist
        if not os.path.exists(path):
            logging.info(f"{debug_prefix} Given path doesn't exist [{path}]")
            sys.exit(-1)

        # Replace on the shader
        self.shader_replace(
            "////ADD_MAPPING",
            f"////ADD_MAPPING\n#pragma use \"{path}\""
        )

    # Maps something to an name inside the shader, please keep track of this name when micro managing the contents.
    def add_mapping(self, name, map_type, path, buffer_width = None, buffer_height = None):
        debug_prefix = "[MMVShaderShadyMaker.add_mapping]"

        # Allowed / existing map types
        map_types = ["image", "audio", "video", "buffer"]

        # Invalid map type
        if not map_type in map_types:
            logging.info(f"{debug_prefix} Map type not in allowed / existing map types {map_types}")
            sys.exit(-1)

        # Buffer mappings need the wdith and height in the end    
        if map_type == "buffer":
    
            # Error assertion, is buffer but no width or height set
            if (buffer_width is None) or (buffer_height is None):
                logging.info(f"{debug_prefix} Buffer width and height cannot be empty for buffer mapping")
                sys.exit(-1)

        # # The mapping syntax

            mapping = f"#pragma map {name}={map_type}:{path};{buffer_width}x{buffer_height}"
        else:
            mapping = f"#pragma map {name}={map_type}:{path}"

        # Path doesn't exist
        if not os.path.exists(path):
            logging.info(f"{debug_prefix} Given path doesn't exist [{path}]")
            sys.exit(-1)

        # Replace on the shader
        self.shader_replace(
            "////ADD_MAPPING",
            f"////ADD_MAPPING\n{mapping}"
        )

    def add_alpha_composite_layer(self, shady_maker, width, height):
        debug_prefix = "[MMVShaderShadyMaker.add_alpha_composite_layer]"
        if self.shader_type == "layer":
            logging.info(f"{debug_prefix} Can't add alpha composite layer for layer shader")

        layer = f"layer{shady_maker.n}"

        self.add_mapping(
            name = layer,
            map_type = "buffer",
            path = shady_maker.path,
            buffer_width = width,
            buffer_height = height,
        )

        self.shader_replace(
            f"{self.indent}////ALPHA_COMPOSITE", (
                f"{self.indent}next_layer = texture2D({layer}, uv);\n"
                f"{self.indent}col = (col * (col.a - next_layer.a)) + (next_layer * (next_layer.a));\n"
                f"\n{self.indent}////ADD_LAYER{layer}_CONTENTS\n{self.indent}////ALPHA_COMPOSITE"
            )
        )

    # Maps something to an name inside the shader, please keep track of this name when micro managing the contents.
    def add_function(self, code):
        debug_prefix = "[MMVShaderShadyMaker.add_function]"

        # Replace on the shader
        self.shader_replace(
            "////ADD_FUNCTIONS", 
            f"{code}\n////ADD_FUNCTIONS"
        )
    
    # Maps something to an name inside the shader, please keep track of this name when micro managing the contents.
    def add_contents(self, code, comment = None, global_shader_target_layer = None):
        debug_prefix = "[MMVShaderShadyMaker.add_contents]"

        code = f"\n{self.indent}".join(code.split("\n"))

        if comment is None:
            comment = ""
        else:
            comment = f"{self.indent}//{comment}\n"

        if global_shader_target_layer is None:
            addcontent = "////ADD_CONTENTS"
        else:
            addcontent = f"////ADD_LAYER{global_shader_target_layer}_CONTENTS"
            
        # Replace on the shader
        self.shader_replace(
            f"{self.indent}{addcontent}", 
            f"{comment}{self.indent}{code}\n{self.indent}////ADD_CONTENTS"
        )

    def camera_transformation(self, code):
        debug_prefix = "[MMVShaderShadyMaker.camera_transformation]"

        self.shader_replace(
            "////CAMERA_TRANSFORMATION",
            f"{code}\n{self.indent}////CAMERA_TRANSFORMATION"
        )
