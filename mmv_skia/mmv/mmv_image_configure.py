"""
===============================================================================

Purpose: MMVImage Configure object, this is mainly a refactor of a .configure
method on MMVImage

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

from mmv.mmv_interpolation import MMVInterpolation
from mmv.mmv_vectorial import MMVVectorial

from mmv.mmv_modifiers import *
import math
import sys


# Configure our main MMVImage, wrapper around animations
class MMVImageConfigure:

    # Get MMVImage object and set image index to zero
    def __init__(self, mmv, mmvimage_object) -> None:
        self.mmv = mmv
        self.object = mmvimage_object
        self.animation_index = 0

    # # # [ Load Image ] # # #

    def load_image(self, path: str) -> None:
        self.object.image.load_from_path(path, convert_to_png=True)

    # # # [ Dealing with animation ] # # #

    # Macros for initializing this animation layer
    def init_animation_layer(self) -> None:
        self.start_or_reset_this_animation()
        self.set_this_animation_steps(steps = math.inf)

    # Make an empty animation layer according to this animation index, dictionaries, RESETS EVERYTHING
    def start_or_reset_this_animation(self) -> None:
        self.object.animation[self.animation_index] = {}
        self.object.animation[self.animation_index]["position"] = {"path": []}
        self.object.animation[self.animation_index]["modules"] = {}
        self.object.animation[self.animation_index]["animation"] = {}

    # Override current animation index we're working on into new index
    def set_animation_index(self, n: int) -> None:
        self.animation_index = n

    # How much steps in this animation  
    def set_this_animation_steps(self, steps: float) -> None:
        self.object.animation[self.animation_index]["animation"]["steps"] = steps

    # Work on next animation index from the current one
    def next_animation_index(self) -> None:
        self.animation_index += 1

    # # # [ Resize Methods ] # # #

    # Resize this Image (doesn't work with Video) to this resolution
    # kwargs: { "width": float, "height": float, "override": bool, False }
    def resize_image_to_resolution(self, **kwargs) -> None:
        self.object.image.resize_to_resolution(
            width = kwargs["width"],
            height = kwargs["height"],
            override = kwargs.get("override", False)
        )

    # kwargs: { "over_resize_width": float, 0, "over_resize_height": float, 0, "override": bool, True}
    # Over resizes mainly because Shake modifier
    def resize_image_to_video_resolution(self, **kwargs) -> None:
        self.resize_image_to_resolution(
            width = self.object.mmv.context.width + kwargs.get("over_resize_width", 0),
            height = self.object.mmv.context.height + kwargs.get("over_resize_height", 0),
            override = kwargs.get("override", True)
        )

    # # # [ Add Methods ] # # #

    """     (MODULE)
        Video module, images will be loaded and updated at each frame
        Please match the input video frame rate with the target FPS
    kwargs: {
        "path": str, Path to load the video
        "width", "height": float
            Width and height to scale the images of the video to (before any modification)
        "over_resize_width", "over_resize_height": float, 0
            Adds to the width and height to resize a bit more, a bleed
    }
    """
    def add_module_video(self, **kwargs):
        self.object.animation[self.animation_index]["modules"]["video"] = {
            "path": kwargs["path"],
            "width": kwargs["width"] + kwargs.get("over_resize_width", 0),
            "height": kwargs["height"] + kwargs.get("over_resize_height", 0),
        }


    """     (PATH)
        Add a Point modifier in the path
    kwargs: {
        x: float, X coordinate
        y: float, Y coordinate
    }
    """
    def add_path_point(self, **kwargs) -> None:
        self.object.animation[self.animation_index]["position"]["path"].append(
            MMVModifierPoint(
                self.mmv,
                y = kwargs["y"], x = kwargs["x"],
            )
        )


    """     (PATH OFFSET)
        Add a shake modifier on the path, remaining approach interpolation
    kwargs: {
        "shake_max_distance": float, max distance on a square we walk on the shake
        "x_smoothness", "y_smoothness": float
            Remaining approach ratio
    }
    """
    def simple_add_path_modifier_shake(self, **kwargs) -> None:
        self.object.animation[self.animation_index]["position"]["path"].append(
            MMVModifierShake(
                self.mmv,
                interpolation_x = MMVInterpolation(
                    self.mmv,
                    function = "remaining_approach",
                    ratio = kwargs["x_smoothness"],
                ),
                interpolation_y = MMVInterpolation(
                    self.mmv,
                    function = "remaining_approach",
                    ratio = kwargs["y_smoothness"],
                ),
                distance = kwargs["shake_max_distance"],
            )
        )

    # # # [ MMVVectorial ] # # #

    """     (MMVVectorial)
    Adds a MMVVectorial with configs on kwargs (piano roll, progression bar, music bars)
    """
    def add_vectorial_by_kwargs(self, **kwargs):
        self.object.animation[self.animation_index]["modules"]["vectorial"] = {
            "object": MMVVectorial(
                self.object.mmv,
                **kwargs,
            )
        }

    """     (MMVVectorial), Music Bars
        Add a music bars visualizer module
    kwargs: configuration, see MMVMusicBarsVectorial class on MMVVectorial
    """
    def add_module_visualizer(self, **kwargs) -> None:
        # Talk to MMVVectorial, say this is a visualizer and add MMVVectorial
        kwargs["vectorial_type_class"] = "visualizer"
        self.add_vectorial_by_kwargs(**kwargs)
        
    """     (MMVVectorial), Progression Bar
        Add a progression bar module
    kwargs: configuration, see MMVProgressionBarVectorial class on MMVVectorial
    """
    def add_module_progression_bar(self, **kwargs) -> None:
        # Talk to MMVVectorial, say this is a progression bar and add MMVVectorial
        kwargs["vectorial_type_class"] = "progression-bar"
        self.add_vectorial_by_kwargs(**kwargs)

    """     (MMVVectorial), Piano Roll
        Add a piano roll module
    kwargs: configuration, see MMVPianoRollVectorial on MMVVectorial
    """
    def add_module_piano_roll(self, **kwargs) -> None:
        # Talk to MMVVectorial, say this is a piano roll and add MMVVectorial
        kwargs["vectorial_type_class"] = "piano-roll"
        self.add_vectorial_by_kwargs(**kwargs)



    # # # [ Modifiers ] # # #


    """     (MMVModifier), Resize
        Resize this object by the average audio value multiplied by a ratio 
    kwargs: {
        "keep_center": bool, True, resize and keep center
        
        "smooth": float, How smooth the resize will be, higher = more responsive, faster
        "scalar": float: The scalar to multiply
            0.5: low
            1:   low-medium
            2:   medium
            3:   medium-plus
            4:   high
            4.5: high-plus
    }
    """
    def add_module_resize(self, **kwargs) -> None:
        self.object.animation[self.animation_index]["modules"]["resize"] = {
            "object": MMVModifierScalarResize(
                self.mmv,
                interpolation = MMVInterpolation(
                    self.mmv,
                    function = "remaining_approach",
                    ratio = kwargs["smooth"],
                ),
                **kwargs
            ),
            "keep_center": kwargs.get("keep_center", True),
        }

    
    """     (MMVModifier), Blur
        Apply gaussian blur with this kernel size, average audio value multiplied by a ratio
    kwargs: {
        "smooth": float, How smooth the blur will be, higher = more responsive, faster
        "scalar": float: The scalar to multiply
            10: low
            15: medium
            20: high
    }
    """
    def add_module_blur(self, **kwargs) -> None:
        self.object.animation[self.animation_index]["modules"]["blur"] = {
            "object": MMVModifierGaussianBlur(
                self.mmv,
                interpolation = MMVInterpolation(
                    self.mmv,
                    function = "remaining_approach",
                    ratio = kwargs["smooth"],
                ),
                **kwargs
            ),
            "keep_center": kwargs.get("keep_center", True),
        }


    # # # [ Rotation ] # # #


    """     (MMVModifier), Rotation
        Add simple swing rotation, go back and forth
    kwargs: {
        "max_angle": float, maximum angle in radians to rotate
        "smooth": float, on each step, add this value to our sinewave point we get the values from
        "phase": float, 0, start the sinewave with a certain phase in radians?
    }
    """
    def add_module_swing_rotation(self, **kwargs) -> None:
        self.object.animation[self.animation_index]["modules"]["rotate"] = {
            "object": MMVModifierSineSwing(self.mmv, **kwargs)
        }


    """     (MMVModifier), Rotation
        Rotate to one direction continuously
    kwargs: {
        "smooth": float, on each step, add this value to our sinewave point we get the values from
        "phase": float, 0, start the sinewave with a certain phase in radians?
    }
    """
    def add_module_linear_rotation(self, **kwargs) -> None:
        self.object.animation[self.animation_index]["modules"]["rotate"] = {
            "object": MMVModifierLinearSwing(self.mmv, **kwargs)
        }


    """     (MMVModifier), Vignetting
        Black borders around the video
    kwargs: {
        "start": float, base value of the vignetting
        "scalar": float, hange the vignetting intensity by average audio amplitude by this
        "minimum": float, hard limit minimum vignette
        "smooth": float, how smooth changing values are on the interpolation
    }
    """
    def add_module_vignetting(self, **kwargs) -> None:
        self.object.animation[self.animation_index]["modules"]["vignetting"] = {
            "object": MMVModifierVignetting(
                self.mmv,
                interpolation = MMVInterpolation(
                    self.mmv,
                    function = "remaining_approach",
                    ratio = kwargs["smooth"],
                ),
                **kwargs
            ),
        }


    # # # # # # # # # # # # # # # DEPRECATED CODE # # # # # # # # # # # # # # #

    # Generic add module #
    def add_module(self, module: dict) -> None:
        module_name = list(module.keys())[0]
        print("Adding module", module, module_name)
        self.object.animation[self.animation_index]["modules"][module_name] = module[module_name]



    # # # # # [ VIGNETTING ] # # # # #

    # Add vignetting module with minimum values
    def ddadd_module_vignetting(self,
            minimum: float,
            interpolation_changer,
            center_function_x,
            center_function_y,
            smooth: float,
            start_value: float,
        ) -> None:

        self.add_module({
            "vignetting": {
                "object": MMVModifierVignetting(
                    context=self.mmv.context,
                    minimum=minimum,
                    center_function_x=center_function_x,
                    center_function_y=center_function_y,
                    interpolation_changer=interpolation_changer,
                    interpolation = MMVInterpolation(
                        self.mmv,
                        function = "remaining_approach",
                        ratio = smooth,
                    ),
                    start_value=start_value,
                ),
            },
        })

    # Just add a vignetting module without much trouble with an intensity
    def simple_add_vignetting(self,
            intensity: str = "medium",
            center: str = "centered",
            center_function_x = None,
            center_function_y = None,
            start_value: float = 900,
            smooth = 0.09,
            custom = None,
        ) -> None:

        intensities = {
            "low": ma_vignetting_ic_low,
            "medium": ma_vignetting_ic_medium,
            "high": ma_vignetting_ic_high,
            "custom": custom
        }
        if intensity not in list(intensities.keys()):
            print("Unhandled resize intensity [%s]" % intensity)
            sys.exit(-1)

        if center == "centered":
            center_function_x = MMVModifierConstant(self.mmv, value = self.object.image.width // 2)
            center_function_y = MMVModifierConstant(self.mmv, value = self.object.image.height // 2)

        self.add_module_vignetting(
            minimum = 450,
            interpolation_changer = intensities[intensity],
            center_function_x = center_function_x,
            center_function_y = center_function_y,
            smooth = smooth,
            start_value = start_value,
        )

 

    # # # # # [ ROTATION ] # # # # #

  