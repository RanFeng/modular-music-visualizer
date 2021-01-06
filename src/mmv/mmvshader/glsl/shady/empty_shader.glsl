// ===============================================================================
//                                 GPL v3 License                                
// ===============================================================================
//
// Copyright (c) 2020,
//   - Tremeschin < https://tremeschin.gitlab.io > 
//
// ===============================================================================
//
// This file was automatically generated by MMVShaderShadyMaker and is intended
// to be run with the Shady project https://github.com/polyfloyd/shady
//
// ===============================================================================
//
// This program is free software: you can redistribute it and/or modify it under
// the terms of the GNU General Public License as published by the Free Software
// Foundation, either version 3 of the License, or (at your option) any later
// version.
//
// This program is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
// FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
// You should have received a copy of the GNU General Public License along with
// this program. If not, see <http://www.gnu.org/licenses/>.
//
// ===============================================================================

////START_MAPPING
////END_MAPPING

////ADD_FUNCTIONS

////ADD_LAYERS

void mainImage(out vec4 fragColor, in vec2 fragCoord)
{
    // Screen coordinate stretching dealing
    vec2 uv = fragCoord.xy / iResolution.xy;
    float screen_ratio_x = iResolution.x / iResolution.y;

    // vec2(0.5, 0.5) is the center of the screen and that is the vec2(0, 0) here
    uv -= 0.5;

    // "Camera" transformation, we transpose every element by adding something to the
    // uv one like set this to [uv += vec2(cos(iIime)/50, sin(iTime/3.34)/45;)]
    // that will give a shaky effect on it. We can also zoom in / zoom out globally
    // by just doing uv *= constant;
    ////CAMERA_TRANSFORMATION

    // Make Y going from 0 - 1 independent on the resolution
    // Note that the X will grow from - aspect ratio/2 to aspect ratio/2
    uv.x *= screen_ratio_x;

    // Return final pixel, replace LAST_LAYER_FUNCTION with the last function
    // of the layer on the chain.
    fragColor = LAST_LAYER_FUNCTION(uv);
}