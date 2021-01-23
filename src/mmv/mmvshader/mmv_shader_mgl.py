"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: 

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

from mmv.common.cmn_constants import STEP_SEPARATOR
from array import array
from PIL import Image
import subprocess
import moderngl
import logging
import cv2
import sys
import re
import os

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Default shader vertex, just accepts an input position, places itself relative to the
# XY plane of the screen and gives us back an uv for the fragment shader
DEFAULT_VERTEX_SHADER = """\
#version 330

// Input / output of coordinates
in vec2 in_pos;
in vec2 in_uv;
out vec2 uv;

// Main function, only assign the position to itself and set the uv coordinate
void main() {
    gl_Position = vec4(in_pos, 0.0, 1.0);
    uv = in_uv;
}"""

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# MMV Specification
# We prefix every fragment shader with this, it's the declaration of uniforms and whatnot
# we also modify, add to it custom ones the user chose.
FRAGMENT_SHADER_MMV_SPECIFICATION_PREFIX = """\
#version 330

// Input and Output of colors
out vec4 fragColor;
in vec2 uv;

// MMV Specification
uniform int mmv_frame;
uniform float mmv_time;
uniform vec2 mmv_resolution;

///add_uniform"""


# Hello world of the fragment shaders
DEFAULT_FRAGMENT_SHADER = """\
void main() {
    fragColor = vec4(uv.x, uv.y, abs(sin(mmv_time/180.0)), 1.0);
}"""

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# When an uniform is not used it doesn't get initialized on the program
# so we .get(name, FakeUniform()) so we don't get errors here
class FakeUniform:
    value = None

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class MMVShaderMGL:
    def __init__(self):
        debug_prefix = "[MMVShaderMGL.__init__]"

        # Create a headless OpenGL context  TODO: support for window mode (performance)?
        self.gl_context = moderngl.create_context(standalone = True)

        # The buffer that represents the 4 points of the screen and their
        # respective uv coordinate. GL center is the coordinate (0, 0) and each
        # edge is either 1 or -1 relative to its axis. We keep that because central rotation
        self.fullscreen_buffer = self.gl_context.buffer(array('f',
            [
            #  (   X,    Y   ) || (   U,    V   )
                -1.0,  1.0,         0.0,  0.0,
                -1.0, -1.0,         0.0,  1.0,
                 1.0,  1.0,         1.0,  0.0,
                 1.0, -1.0,         1.0,  1.0,
            ]
            # [
            # #  (   X,    Y   ) || (   U,    V   )
            #     -1.0,  1.0,        -1.0,  1.0,
            #     -1.0, -1.0,        -1.0, -1.0,
            #      1.0,  1.0,         1.0,  1.0,
            #      1.0, -1.0,         1.0, -1.0,
            # ]
        ))

        # Info we send to the shaders
        self.pipeline = {
            "mmv_time": 0,
            "mmv_frame": 0,
            "mmv_resolution": [0, 0],
        }
        self.textures = {}
        self.shaders_as_textures = []

    # Configurate how we'll output the shader
    def render_config(self, width, height, fps):
        debug_prefix = "[MMVShaderMGL.config]"
        (self.width, self.height, self.fps) = (width, height, fps)
        
    # Create one FBO which is a texture under the hood so we can utilize it in some other shader
    def construct_texture_fbo(self):
        texture = self.gl_context.texture((self.width, self.height), 4)
        fbo = self.gl_context.framebuffer(color_attachments = [texture])
        return [texture, fbo]

    # Create one context's program out of a frag and vertex shader, those are used together
    # with VAOs so we render to some FBO
    def construct_shader(self, fragment_shader = DEFAULT_FRAGMENT_SHADER, vertex_shader = DEFAULT_VERTEX_SHADER):
        debug_prefix = "[MMVShaderMGL.construct_shader]"

        # The raw specification prefix, sets uniforms every one should have
        # we don't add just yet to the fragment shader because we can have some #pragma map
        # and we have to account for that before compiling the shader
        fragment_shader_prefix = FRAGMENT_SHADER_MMV_SPECIFICATION_PREFIX

        # # Parse the shader

        logging.info(f"{debug_prefix} Parsing the fragment shader for every #pragma map")

        # Regular expression to match #pragma map name=loader:/path/value;512x512
        # the ;512x512 is optional and only used with the shader loader
        regex = r"#pragma map ([\w]+)=([\w]+):([\w/. -]+):?([0-9]+)?x?([0-9]+)?"
        found = re.findall(regex, fragment_shader)

        # The static uniforms we'll assign the values
        assign_static_uniforms = []

        # For each mapping
        for mapping in found:
            name, loader, value, width, height = mapping
            logging.info(f"{debug_prefix} Matched mapping [name={name}] [loader={loader}] [width={width}] [height={height}]")

            # Error assertion, valid loader and path
            loaders = ["image", "video", "shader", "use"]
            assert loader in loaders, f"Loader not implemented in loaders {loaders}"
            assert os.path.exists(value), f"Value of loader [{value}] is not a valid path"

            # We'll map one texture
            if loader in ["image", "shader", "video"]:
                print(found)
                assert (width != '') and (height != ''), "Width or height shouldn't be null, set WxH on pragma map with ;512x512"

                # Image loader
                if loader == "image":
                    # Load the image, get width and height for the texture size
                    img = Image.open(value).convert("RGBA")
                    width, height = img.size

                    # Upload the texture to the GPU
                    logging.info(f"{debug_prefix} Uploading texture to the GPU")
                    texture = self.gl_context.texture((width, height), 4, img.tobytes())

                    self.textures[len(self.textures.keys()) + 1] = [name, "texture", texture]
                    
                # Add shader as texture element
                elif loader == "shader":

                    with open(value, "r") as f:
                        loader_frag_shader = f.read()

                    shader_as_texture = MMVShaderMGL()
                    shader_as_texture.render_config(width = int(width), height = int(height), fps = None)
                    texture, fbo = shader_as_texture.construct_texture_fbo()
                    shader_as_texture.construct_shader(fragment_shader = loader_frag_shader)
                    self.shaders_as_textures.append(shader_as_texture)

                    self.textures[len(self.textures.keys()) + 1] = [name, "shader", shader_as_texture.texture]

                elif loader == "video":
                    video = cv2.VideoCapture(value)
                    self.textures[len(self.textures.keys()) + 1] = [name, "video", video]
                    
                # Add the texture uniform values
                marker = "///add_uniform"
                fragment_shader_prefix = fragment_shader_prefix.replace(f"{marker}", f"\n// Texture\n{marker}")
                fragment_shader_prefix = fragment_shader_prefix.replace(f"{marker}", f"uniform sampler2D {name};\n{marker}")
                fragment_shader_prefix = fragment_shader_prefix.replace(f"{marker}", f"uniform int {name}_width;\n{marker}")
                fragment_shader_prefix = fragment_shader_prefix.replace(f"{marker}", f"uniform int {name}_height;\n{marker}\n")
                fragment_shader_prefix = fragment_shader_prefix.replace(f"{marker}", f"uniform vec2 {name}_resolution;\n{marker}\n")
    
                # The attributes we'll put into the previous values
                assign_static_uniforms += [
                    [f"{name}_width", int(width)],
                    [f"{name}_height", int(height)],
                    [f"{name}_resolution", (int(width), int(height))],
                ]

        # Get #pragma includes

        regex = r"#pragma include ([\w/. -]+)"
        found = re.findall(regex, fragment_shader)

        # For each mapping
        for include in found:
            replaces = f"#pragma include {include}"
            
            assert os.path.exists(include), f"Value of #pragma include is not a valid path [{include}]"

            with open(include, "r") as f:
                include_other_glsl_data = f.read()

            fragment_shader = fragment_shader.replace(replaces, include_other_glsl_data)
            

        # We parsed the body and added to the prefix stuff that was defined so merge everything together
        fragment_shader = f"{fragment_shader_prefix}\n{fragment_shader}"

        # # Construct the shader

        # Create a program and return it
        self.program = self.gl_context.program(fragment_shader = fragment_shader, vertex_shader = vertex_shader)
        self.vao = self.gl_context.vertex_array(self.program, [(self.fullscreen_buffer, '2f 2f', 'in_pos', 'in_uv')])
        self.texture, self.fbo = self.construct_texture_fbo()
 
        # Assign the VAO
        self.vao = self.gl_context.vertex_array(self.program, [(self.fullscreen_buffer, '2f 2f', 'in_pos', 'in_uv')])

        # Assign the uniforms to blank value
        for name, value in assign_static_uniforms:
            print(name, value)
            uniform = self.program.get(name, FakeUniform())
            uniform.value = value

        import shutil
        s = "-" * shutil.get_terminal_size()[0]
        print(f"{s}\n{fragment_shader}")
        print(f"{s}\n{vertex_shader}\n{s}")

    # Pipe a pipeline to a target that have a program attribute
    def pipe_pipeline(self, pipeline, target):
        debug_prefix = "[MMVShaderMGL.pipe_pipeline]"

        # Pass the pipeline values to the shader
        for key, value in pipeline.items():
            uniform = target.program.get(key, FakeUniform())
            uniform.value = value
            
    # Render this shader to the FBO recursively
    def render(self, pipeline):
        debug_prefix = "[MMVShaderMGL.render]"

        # Render every shader as texture recursively
        for shader_as_texture in self.shaders_as_textures:
            self.pipe_pipeline(pipeline = pipeline, target = shader_as_texture)
            shader_as_texture.render(pipeline = pipeline)

        # Pipe the pipeline to self
        self.pipe_pipeline(pipeline = pipeline, target = self)

        # Render to the FBO using this VAO
        self.fbo.use()
        self.fbo.clear()

        # The location is the dict index, the texture info is [name, loader, object]
        for location, texture_info in self.textures.items():
            name = texture_info[0]
            loader = texture_info[1]
            tex_obj = texture_info[2]

            try:
                # Read the next frame of the video
                if loader == "video":
                    ok, frame = tex_obj.read()

                    # Can't read, probably out of frames?
                    if not ok:  # cry

                        #reset to frame 0
                        tex_obj.set(cv2.CAP_PROP_POS_FRAMES, 0)

                        # Read again
                        ok, frame = tex_obj.read()
                    
                    # Flip the image TODO: flip in GLSL by inverting uv?
                    # frame = cv2.flip(frame, 0)
                    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_texture = self.gl_context.texture((frame.shape[1], frame.shape[0]), 3, frame)
                else:
                    frame_texture = tex_obj

                # Set the location we'll expect this texture
                self.program[name] = location
                
                # Use it
                frame_texture.use(location = location)
            
            # Texture wasn't used, should error out on self.program[name]
            except KeyError:
                pass

        # Render to this class FBO
        self.vao.render(mode = moderngl.TRIANGLE_STRIP)

    # Iterate through this class instance as a generator for getting the 
    def next(self, custom_pipeline = {}):
        self.pipeline["mmv_frame"] += 1
        self.pipeline["mmv_time"] = round((self.pipeline["mmv_frame"] / self.fps), 3)

        self.pipeline["mmv_resolution"] = (self.width, self.height)

        # Assign user custom pipelines
        for key, value in custom_pipeline.items():
            self.pipeline[key] = value

        # print(self.pipeline)
        self.render(pipeline = self.pipeline)
            
    def read(self):
        return self.fbo.read()