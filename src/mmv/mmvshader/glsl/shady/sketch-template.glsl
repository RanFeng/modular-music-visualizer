// ===============================================================================
//                                 GPL v3 License                                
// ===============================================================================
//
// Copyright (c) 2020,
//   - Tremeschin < https://tremeschin.gitlab.io > 
//
// ===============================================================================
//
// Purpose: Sketch template for automating writing GLSL shaders
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

// #pragma map image1=image:path
#pragma map image2=image:path
#pragma map image1=video:path
// #pragma map audio=audio:path


// Blit one image on the canvas at a certain rotation angle, scale
vec4 blitimage(in vec4 canvas, in sampler2D image, in vec3 imagesize, in vec2 uv, in vec2 anchor, in float scale, in float angle) {
    
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

    // Get the texture
    vec4 imagepixel = textureLod(
        image,
        rotation_matrix * scale_mateix * (uv + anchor) * vec2(1.0, -1.0),
        1.0
    );

    return imagepixel;
}

vec4 layer1(in vec2 uv) {
    float scale = (0.5 * atan(iTime / 4.0)) + 0.1;
    float angle = sin(iTime)/10.0;
    vec4 layercolor = vec4(0.);
    layercolor = blitimage(
        layercolor, image1, image1Size,
        uv, vec2(0.0, 0.0), scale, angle
    );
    return layercolor;
}

vec4 layer2(in vec2 uv) {
    float scale = (0.8 * atan(iTime)) + 0.1;
    float angle = cos(iTime/3.0)/3.0;
    vec4 layercolor = vec4(0.);
    layercolor = blitimage(
        layercolor, image2, image2Size,
        uv, vec2(0.0, 0.0), scale, angle
    );
    layercolor.a = clamp(pow(1.0 - length(uv), 4.0), 0.0, 1.0);
    return layercolor;
}


void mainImage(out vec4 fragColor, in vec2 fragCoord)
{
    // Screen coordinate stretching dealing
    vec2 uv = fragCoord.xy / iResolution.xy;
    float screen_ratio_x = iResolution.x / iResolution.y;
    uv -= 0.5;
    uv.x *= screen_ratio_x;

    float zoom = 2.0 + sin(iTime / 2.2123513);
    uv *= zoom;


    // This and next layer placeholders
    vec4 col = vec4(0.0);
    vec4 next_layer = vec4(0.0);


    // // // Layer 1

    // // [Layer 1] Main routine
    next_layer = layer1(uv);

    // [Layer 1] Effects
    // [Layer 1] Chromatic Aberration
    float ca_amount = sin(iTime);
    vec2 car = vec2(ca_amount *  0.01 * cos(iTime),     ca_amount *  0.01 * sin(iTime));
    vec2 cag = vec2(ca_amount *  0.01 * sin(iTime * 2.0), ca_amount * -0.01 * cos(iTime / 4.0));
    vec2 cab = vec2(ca_amount * -0.01 * sin(iTime * 3.0), ca_amount * -0.01 * cos(iTime * 5.0));
    vec4 next_layerr = layer1(uv + car);
    vec4 next_layerg = layer1(uv + cag);
    vec4 next_layerb = layer1(uv + cab);
    next_layer = vec4(next_layerr.r, next_layerg.g, next_layerb.b, next_layer.a);
    // [Layer 1] Chromatic Aberration
    // [Layer 1] End Effects

    col = (col * (1.0 - next_layer.a)) + (next_layer * next_layer.a);
    // // [Layer 2] End Main routine


    // // // Layer 2

    // // [Layer 2] Main routine
    next_layer = layer2(uv);
    // [Layer 2] Effects
    // [Layer 2] End Effects
    col = (col * (1.0 - next_layer.a)) + (next_layer * next_layer.a);
    // // [Layer 2] End Main routine


    // // // // Output

    fragColor = vec4(col);
}


