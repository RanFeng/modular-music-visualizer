"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Basic usage example of MMV

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

import sys
import os

# Append previous folder to path
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append("..")
sys.path.append(
    THIS_DIR + "/../"
)

import mmv.common.cmn_any_logger
import logging
import typer

app = typer.Typer(chain = True)


class MMVCliInterface:
    def __init__(self):
        self.mmv_interface = None
        self.mmv_skia_interface = None
        self.mmv_shader_interface = None
        self.video_encoder = None

        # What interface we're targeting and using right now?
        # We share some commands with both like setting up video quality
        # and whatnot
        self.USING = None

        # Target outputs
        self.height = None
        self.width = None
        self.fps = None

    # Iinitialize the top level MMVInterface
    def init_mmv_interface(self):
        import mmv
        self.mmv_interface = mmv.MMVInterface()

    # FIXME: Required? user  must have typer an all for executing this anyway
    def install_requirements(self):
        from modules.end_user_utilities import Requirements
        requirements = Requirements()
        requirements.install()

    # Init some MMV interface, shader or skia
    def init(self, who: str = typer.Option("skia", help = "Possible values are [skia, shader]")):
        """
        Initialize some MMV interface out of the many ones that can exist, see --who argument options
        """
        if not who in ["skia", "shader"]:
            raise RuntimeError(f"Not valid init interface for [{who}] in [skia, shader]")

        # Initialize global MMV interface if it's not done
        if self.mmv_interface is None:
            self.init_mmv_interface()
        
        # Initialize what interface and set self.USING to that one
        if who == "skia":
            self.mmv_skia_interface = self.mmv_interface.get_skia_interface()
            self.mmv_skia_interface.audio_processing.preset_balanced()
            self.skia_globals()
            self.USING = "skia"
        elif who == "shader":
            self.mmv_shader_interface = self.mmv_interface.get_shader_interface()
            self.USING = "shader"
    
    def __ensure_mmv_interface(self):
        if self.mmv_interface is None:
            raise RuntimeError("Please initialize MMVInterface first with command [init] and preferably who, see init --help")

    def __ensure_mmv_skia_interface(self):
        if self.mmv_skia_interface is None:
            raise RuntimeError("Please initialize MMVSkiaInterface first with command [init skia]")

    def __ensure_mmv_shader_interface(self):
        if self.mmv_shader_interface is None:
            raise RuntimeError("Please initialize MMVShaderInterface first with command [init shader]")
    
    def __ensure_video_encoder(self):
        if self.video_encoder is None:
            raise RuntimeError("Please initialize one Video Encoder (FFmpegWrapper) with the [encoding --help] command first.")

    # # Shared methods

    def ensure_ffmpeg(self,
        force: bool = typer.Option(False, help = "If on Linux download the FFmpeg Windows binaries anyways"),
    ):
        """
        Attempts to download FFmpeg and move to the externals folder. Doesn't work on Linux and macOS, please install it
        from yours distro package manager or macOS homebrew. This is absolutely required for running MMVSkia or MMVShader
        Shady interface. MMVShaderMPV does not require it but only works on Linux rendering videos to files.
        """
        debug_prefix = "[MMVCliInterface.ensure_ffmpeg]"
        self.__ensure_mmv_interface()
        logging.info(f"{debug_prefix} Ensure FFmpeg, force = [{force}")
        self.mmv_interface.download_check_ffmpeg(making_release = force)

    def ensure_mpv(self,
        force: bool = typer.Option(False, help = "If on Linux download the MPV Windows binaries anyways"),
    ):
        """
        Attempts to download MPV and move to the externals folder. Doesn't work on Linux and macOS, please install it
        from yours distro package manager or macOS homebrew.
        """
        debug_prefix = "[MMVCliInterface.ensure_mpv]"
        self.__ensure_mmv_interface()
        logging.info(f"{debug_prefix} Ensure MPV, force = [{force}")
        self.mmv_interface.download_check_mpv(making_release = force)

    def ensure_musescore(self,
        force: bool = typer.Option(False, help = "If on Linux download the Musescore Windows binaries anyways"),
    ):
        """
        Attempts to download Musescore portable and move to the externals folder. Doesn't work on Linux and macOS, please install it
        from yours distro package manager or macOS homebrew. Used for converting MIDI files to Audio files
        """
        debug_prefix = "[MMVCliInterface.ensure_musescore]"
        self.__ensure_mmv_interface()
        logging.info(f"{debug_prefix} Ensure Musescore, force = [{force}")
        self.mmv_interface.download_check_musescore(making_release = force)

    def resolution(self,
        width: int = typer.Option(None, help = "Output resolution width (horizontal pixel count)"),
        height: int = typer.Option(None, help = "Output resolution height (vertical pixel count)"),
        fps: float = typer.Option(60, help = "Output frame rate in Frames Per Seconds (FPS)"),
        preset: str = typer.Option(None, help = (
            "Ignore above options, use presets in common resolutions in any combinations of: [RATIO-HEIGHT-FPS] "
            "[{16:9, 19:9, 21:9}{2160p, 1440p, 1080p, 720p, 480p}{144, 60, 30, 24}]. "
            "Example for common 16:9 ones: 1080p,60 (16:9 is implied by default), Ultrawide FHD 144 Hz: 21:9,1080p,144. "
            "Setting a width or height or fps will override the preset"
        ))
    ):
        """
        Configure the resolution options (width, height, fps) manually or write a short hand preset like [1080p,60] or [21:9,1440p,144]
        """
        debug_prefix = "[MMVCliInterface.resolution]"

        # User has set some preset
        if preset is not None:

            preset = preset.replace(" ", "")

            # Imply 16:9
            if not ":" in preset:
                preset = f"16:9,{preset}"
                
            # Sketchy marketing naming
            if "21:9" in preset:
                preset = preset.replace("21:9", "64:27")

            # Split into
            data = preset.split(",")

            # Malformatted data..
            if len(data) != 3:
                raise RuntimeError((
                "Malformatted output format preset, please use [aspect ratio]-[resolution p]-[fps] like 16:9-1080p-60 "
                "or 21:9-1440p-144, NOTE: 720p-60 already implies 16:9 aspect ratio"
            ))

            # Split 16:9 in 16 and 9
            ratio = data[0].split(':')
            ratio_multiplier  = float(ratio[0])
            ratio_denominator = float(ratio[1])

            # 'p', the height or something
            p = int(data[1].replace('p', ""))
            preset_fps = int(data[2])

            # Can already set to the height
            self.height = p
            self.width = int(p * (ratio_multiplier/ratio_denominator))
            self.fps = preset_fps
        else:
            # No preset set and some width, height or fps are empty
            if any([option is None for option in [width, height, fps]]):
                raise RuntimeError((
                    "No output format preset set and also didn't set all width, height or fps. "
                    "Please use preset or give the three settings"
                ))
        
        # Overwrite width, height or fps
        if width is not None:
            self.width = width
            logging.info(f"{debug_prefix} Overwriting MMVCliInterface width to [{width}]")
        if height is not None:
            self.height = height
            logging.info(f"{debug_prefix} Overwriting MMVCliInterface height to [{height}]")
        if fps is not None:
            self.fps = fps
            logging.info(f"{debug_prefix} Overwriting MMVCliInterface fps to [{fps}]")

        # Warn final targets
        logging.info(f"{debug_prefix} Final [width = {self.width}, height = {self.height}, fps = {self.fps}]")
    
    def encoding(self,
        input_audio: str = typer.Option(None, help = (
            "Audio we add on the final video, set to None for no audio"
        )),

        output_video: str = typer.Option(None, help = (
            "Final video we render to. We highly recommend outputting to a .mkv format as you don't have to "
            "wait for the whole render process to finish so you can see the results (matroska video progressively "
            "writes the information and don't need to enclose the container before being able to decode)"
        )),

        preset: str = typer.Option("slow", help = (
            "Encoder preset, possible values are:\n"
            " > [placebo, veryslow, slowest, slow,\n"
            "    medium, fast, faster, veryfast,zn\n"
            "    superfast, ultrafast]\n"
            "\n"
            "Slower presets yields a higher quality encoding but utilize more CPU, "
            "since MMVSkia is by no means no realtime, a slow preset should be enough since "
            "the FFmpeg process is run in parallel."
        )),

        crf: int = typer.Option(17, help = (
            "Constant Rate Factor of x264 or x265 encoding, 0 is lossless, 51 is the worst, "
            "23 the the default. Low values means higher quality and bigger file size."
        )),

        tune: str = typer.Option("film", help = (
            "Tune video encoder for:\n"
            "film:       Mostly IRL stuff, shouldn't hurt letting this default\n"
            "animation:  Animes in general, we use this default as\n"
            "grain:      Optimized for old / grainy contents for preserving it\n"
            "fastdecode: For low compute power devices to have less trouble with\n"
        )),

        hwaccel: str = typer.Option("auto", help = ("Try utilizing hardware acceleration? Set to None for ignoring this")),

        input_pix_fmt: str = typer.Option("rgba", help = (
            "Expected pixel format we get from Skia or Shady, if you get wrong color outputs try changing to [bgra]"
        )),
    ):
        """
        Create an "Video Encoder" class (FFmpegWrapper) with the settings configured before like resolution, fps.
        We try to find the FFmpeg binary on the Externals directory and the system's PATH variable.
        If you're on windows add before this command [ensure-ffmpeg] and it should take care of itself. Linux and
        macOS users please install it from your distro / package manager (apt, brew, pacman, zypper, etc)
        """
        debug_prefix = "[MMVCliInterface.encoding]"
        if any([option is None for option in [self.width, self.height, self.fps]]):
            raise RuntimeError("Please set target output resolution and fps first with the [resolution --help] command!!")
        
        # Error assertion, output video must not be none
        if output_video is None:
            raise RuntimeError("Output video cannot be None. Add one with the --output-video flag")

        # Get one FFmpegWrapper class and configure it
        self.video_encoder = self.mmv_interface.get_ffmpeg_wrapper()
        self.video_encoder.configure_encoding(
            ffmpeg_binary_path = self.mmv_interface.find_binary("ffmpeg"),
            width = self.width,
            height = self.height,
            input_audio_source = input_audio,
            input_video_source = "pipe",  # FIXME: we pretty much always use pipe, will we ever need to change this?
            output_video = output_video,
            pix_fmt = input_pix_fmt,
            framerate = self.fps,
            preset = preset,
            hwaccel = hwaccel,

            # Don't overflow the subprocess buffer
            loglevel = "panic",
            nostats = True,
            hide_banner = True,

            # If True adds "-x264opts opencl" to the FFmpeg command. Can make FFmpeg have a
            # startup time of a few seconds, will disable for compatibility since not everyone
            # have opencl loaders, etc.
            opencl = False,  # FIXME: Leaving as False..
            crf = crf,
            tune = tune,
            vcodec = "libx264",
            override = True,
        )

        # Assign the Video encoder to the USING interface
        if self.USING == "skia":
            logging.info(f"{debug_prefix} User is working with Skia interface, so sending this video encoder to MMVSkiaInterface and configuring input audio / output video")
            self.mmv_skia_interface.set_mmv_skia_video_encoder(self.video_encoder)

            self.mmv_skia_interface.input_audio(input_audio)
            self.mmv_skia_interface.output_video(output_video)


    # # # Skia methods

    def skia_globals(self,
        audio_amplitude_multiplier: float = typer.Option(1.0, help = (
            "If your audio isn't properly normalized or you want a more aggressive video, et this to 1.5 - 2 or so. "
            "This option multiplies the absolute then average audio amplitude MMVSkiaCore modulator by this much."    
        )),
        render_backend: str = typer.Option("gpu", help = (
            "Use or not a GPU accelerated context, pass render=gpu or render=cpu flag "
            "For higher resolutions 720p+, GPUs are definitely faster for raw output "
            "but for smaller res, CPUs win on image transfering, it defaults to GPU "
            "on the final video render if no flag was passed. Generating images such as "
            "particles and backgrounds is done on CPU as no textures are being moved."
        )),
        max_images_on_pipe_buffer: int = typer.Option(20, help = (
            "How many max images to hold on a list of images to pipe? Usually shouldn't get big unless you have a really "
            "bad CPU and it's bottlenecking the whole thing. Usually will happen when there is a lot stuff going on on the "
            "screen so don't really worry of this option I guess."
        ))
    ):
        """
        Configure some variables that are useful to tinker with not directly needing their own category
        """
        debug_prefix = "[MMVCliInterface.resolution]"
        self.__ensure_mmv_skia_interface()

        logging.info(f"{debug_prefix} Set [audio_amplitude_multiplier={audio_amplitude_multiplier}, render_backend={render_backend}, max_images_on_pipe_buffer={max_images_on_pipe_buffer}]")

        self.mmv_skia_interface.configure_mmv_skia_main(
            audio_amplitude_multiplier = audio_amplitude_multiplier,
            render_backend = render_backend,
            max_images_on_pipe_buffer = max_images_on_pipe_buffer,
        )

    # Configure the FFT on the Skia interface
    def skia_fft(self,
        batch_size: int = typer.Option(2048, help = (
            "The window size of the FFT (Fast Fourier Transform), generally speaking lower values yields less information "
            "on the frequencies and less precise music bars, though it is a O(N log N) \"expensive\" function, higher values "
            "will also require more computing power but gives more precise bars. MMV calculates the FFTs of both left and "
            "right channel as well as repeat this process with both channels downsampled so we get more bass information. "
            "A value of 2048 should be ok for the majority of cases, use 8192 at max I'd say (also prefer multiples of 2)."  
        ))
    ):
        """
        Configure FFT related stuff.
        """
        debug_prefix = "[MMVCliInterface.skia_fft]"

        logging.info(f"{debug_prefix} Set MMVSkiaInterface FFT batch size to [{batch_size}]")

        self.mmv_skia_interface.fft(
            batch_size = batch_size
        )


# This wouldn't be required but Windows :p
if __name__ == "__main__":
    cli = MMVCliInterface()

    # Common / QOL
    app.command()(cli.install_requirements)
    app.command()(cli.init)

    # Shared
    app.command()(cli.resolution)
    app.command()(cli.ensure_ffmpeg)
    app.command()(cli.ensure_mpv)
    app.command()(cli.ensure_musescore)
    app.command()(cli.encoding)

    # Skia specific
    app.command()(cli.skia_globals)
    app.command()(cli.skia_fft)


    # Run the CLI app
    app()
