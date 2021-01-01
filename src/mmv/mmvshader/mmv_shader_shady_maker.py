"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Utility to wrap around mpv and add processing shaders, target
resolutions, input / output

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
        self.added_layers = []
    
    # Get the empty shader, add the mmv-specifications.glsl file
    def empty_shader(self):
        sep = os.path.sep
        with open(f"{self.mmv_shader_main.interface.SHADERS_LOCATED_AT}{sep}shady{sep}empty_shader.glsl", "r") as f:
            self.shader = f.read()
        self.use_shader(f"{self.mmv_shader_main.interface.SHADERS_LOCATED_AT}{sep}shady{sep}mmv_specification.glsl")
    
    # DEBUG, show what is being written
    def shader_replace(self, old, new):
        debug_prefix = "[MMVShaderShadyMaker.add_mapping]"

        # Debug what we're changing
        print(f"{debug_prefix} Replacing on the shader")
        print(f"{debug_prefix} [OLD] {old}")
        print(f"{debug_prefix} [NEW] {new}")

        # Replace on the shader
        self.shader = self.shader.replace(old, new)
    
    # DEBUG Write the current shader to the runtime directory
    def write_current_shader(self):
        runtime = self.mmv_shader_main.context.directories.runtime
        n = len(os.listdir(runtime))
        save_path = f"{runtime}{os.path.sep}{n} [DEBUG SHADER].glsl"
        with open(save_path, "w") as f:
            f.write(self.shader)
        return save_path

    # Add #pragma use "path" to the mappings on a shader (usually importing MMV specifications)
    def use_shader(self, path):
        debug_prefix = "[MMVShaderShadyMaker.use_shader]"

        # Path doesn't exist
        if not os.path.exists(path):
            print(f"{debug_prefix} Given path doesn't exist [{path}]")
            sys.exit(-1)

        # Replace on the shader
        self.shader_replace(
            "////END_MAPPING", (
                f"#pragma use \"{path}\"\n"
                "////END_MAPPING"
            )
        )

    # Maps something to an name inside the shader, please keep track of this name when micro managing the contents.
    def add_mapping(self, name, map_type, path):
        debug_prefix = "[MMVShaderShadyMaker.add_mapping]"

        # Allowed / existing map types
        map_types = ["image", "audio", "video"]

        # Invalid map type
        if not map_type in map_types:
            print(f"{debug_prefix} Map type not in allowed / existing map types {map_types}")
            sys.exit(-1)

        # Path doesn't exist
        if not os.path.exists(path):
            print(f"{debug_prefix} Given path doesn't exist [{path}]")
            sys.exit(-1)

        # Replace on the shader
        self.shader_replace(
            "////END_MAPPING", (
                f"#pragma map {name}={map_type}:{path}\n"
                "////END_MAPPING"
            )
        )

    def add_layer(self, layer_number, alpha_composite = True):
        debug_prefix = "[MMVShaderShadyMaker.add_layer]"

        # Can't add duped layer, function names will overlap
        if layer_number in self.added_layers:
            print(f"{debug_prefix} Already added layer N={layer_number}")
            sys.exit()

        self.added_layers.append(layer_number)

        last_layer = f"vec4 previous_layer = layer{layer_number - 1}(uv);"
        alpha_composite_code = "layercolor = (previous_layer * (previous_layer.a - layercolor.a)) + (layercolor * (layercolor.a));"

        if (layer_number == 1):
            last_layer = "// Last Layer doesn't exist, this is the first one"
            alpha_composite_code = "// Can't alpha composite with the last layer"
        
        if not alpha_composite:
            alpha_composite_code = "// Disabled alpha composite"

        self.shader_replace(
            "////ADD_LAYERS",
f"""\
vec4 layer{layer_number}(in vec2 uv) {{
    vec4 layercolor = vec4(0.);
    {last_layer}
    ////LAYER_{layer_number}_CONTENTS
    {alpha_composite_code}
    return layercolor;
}}\n
////ADD_LAYERS"""
        )

    # Replace LAST_LAYER_FUNCTION with the layer{max(N)} function
    def hook_last_layer_to_output(self, multi_sample = 1):
        debug_prefix = "[MMVShaderShadyMaker.add_layer]"

        # Get the maxlayer
        maxlayer = max(self.added_layers)
        print(f"{debug_prefix} Max layer number added is [{maxlayer}]")

        # Replace on the shader
        self.shader_replace(
            "LAST_LAYER_FUNCTION",
            f"layer{maxlayer}"
        )
    
    def camera_transformation(self, code):
        debug_prefix = "[MMVShaderShadyMaker.camera_transformation]"

        self.shader_replace(
            "////CAMERA_TRANSFORMATION",
            code
        )

    # Add a block of code to this layer number content
    # Replaces PREV_LAYER with the previous layer function if layer number is greater than 1
    def add_layer_content(self, layer_number, code):
        debug_prefix = "[MMVShaderShadyMaker.add_layer]"

        # Annoying variables names
        layer_contents_string = f"    ////LAYER_{layer_number}_CONTENTS"
        prev_layer_function = f"layer{layer_number - 1}"

        # Replace previous layer get methods / functions
        if layer_number > 1:
            print(f"{debug_prefix} Replace block of code PREV_LAYER with [{prev_layer_function}]")
            code = code.replace("PREV_LAYER", prev_layer_function)
    
        # Debug
        print(f"{debug_prefix} Add layer content at layer N={layer_number}, block of code:")
        print(f"{debug_prefix} {code}")

        # Replace on the shader
        self.shader_replace(
            layer_contents_string,
            f"{code}\n{layer_contents_string}"
        )
        