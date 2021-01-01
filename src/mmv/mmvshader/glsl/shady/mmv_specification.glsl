// ===============================================================================
//                                 GPL v3 License                                
// ===============================================================================
//
// Copyright (c) 2020,
//   - Tremeschin < https://tremeschin.gitlab.io > 
//
// ===============================================================================
//
// Purpose: MMV specifications that are imported when making one main GLSL file
// for rendering
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


// Blit one image on the canvas, see function arguments
vec4 mmv_blit_image(
        in vec4 canvas,     // Return this if out of bounds and repeat = false
        in sampler2D image, // The texture
        in vec3 imagesize,  // As Shady adds {mapping}Size for the ratios, give those
        in vec2 uv,         // UV we're getting (usually the layer's uv)
        in vec2 anchor,     // Anchor the rotation on the screen in some point
        in vec2 shift,      // Shift the image (for example vec2(0.5, 0.5) will rotate around the center)
        in float scale,     // Scale of the image 1 = 100%, 2 = 200%
        in float angle,     // Angle of rotation, be aware of aliasing!
        in bool repeat)     // If out of bounds tile the image?
    {
    
    // Image ratios
    float image_ratio_x = imagesize.x / imagesize.y;
    float image_ratio_y = imagesize.y / imagesize.x;

    // Scale matrix
    mat2 scale_mateix = mat2(
        (1.0 / scale), 0,
        0, (1.0 / scale)
    );

    // Rotation Matrix
    float c = cos(angle);
    float s = sin(angle);
    mat2 rotation_matrix = mat2(
         c * image_ratio_y, s * image_ratio_x,
        -s, c
    );

    // The rotated, scaled and anchored, flipped and shifted UV coordinate to get this sampler2D texture
    vec2 get_image_uv = (rotation_matrix * scale_mateix * (uv + anchor) * vec2(1.0, -1.0)) + shift;

    // If not repeat, check if any uv is out of bounds
    if (! repeat) {
        if (get_image_uv.x < 0.0) { return canvas; }
        if (get_image_uv.x > 1.0) { return canvas; }
        if (get_image_uv.y < 0.0) { return canvas; }
        if (get_image_uv.y > 1.0) { return canvas; }
    }

    // Get the texture
    vec4 imagepixel = textureLod(
        image, get_image_uv, 1.0
    );

    // Return the texture
    return imagepixel;
}


// // Useful function

// https://gist.github.com/patriciogonzalezvivo/670c22f3966e662d2f83
float rand(float n){return fract(sin(n) * 43758.5453123);}
