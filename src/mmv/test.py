import sys
import os

# Append previous folder to path
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append("..")
sys.path.append(
    THIS_DIR + "/../"
)

# Import mmv, get interface
import mmv
interface = mmv.MMVInterface()

# Testing
interface.download_check_ffmpeg(making_release = True)
interface.download_check_mpv(making_release = True)
interface.download_check_musescore(making_release = True)

# Shader interface >:)
mmv_shader_interface = interface.get_shader_interface()
shady = mmv_shader_interface.mmv_shader_main.shady
shady_maker = mmv_shader_interface.mmv_shader_main.shady_shader_maker

WIDTH = 1280
HEIGHT = 720
FRAMERATE = 60
supersampling = 1

sep = os.path.sep

# #

shady.base_configuration(
    shady_binary = interface.find_binary("shady"),
    width = int(WIDTH * supersampling),
    height = int(HEIGHT * supersampling),
    framerate = FRAMERATE,
    main_glsl = f"{THIS_DIR}/mmvshader/glsl/shady/layer2.glsl",
)

# # Visualize / render

if "render" in sys.argv:
    # Video encoder
    video_encoder = interface.get_ffmpeg_wrapper()
    video_encoder.configure_encoding(
        ffmpeg_binary_path = interface.find_binary("ffmpeg"),
        width = int(WIDTH * supersampling),
        height = int(HEIGHT * supersampling),
        input_audio_source = None,
        input_video_source = "pipe",
        output_video = f"{THIS_DIR}/../mmvshady.mp4",
        pix_fmt = "rgba",
        framerate = FRAMERATE,
        preset = "fast",
        hwaccel = "auto",
        loglevel = "",
        nostats = False,
        hide_banner = True,
        opencl = False,
        crf = 18,
        tune = "film",
        vcodec = "libx264",
        override = True,
        t = 30,
        vflip = True,
        scale = f"{WIDTH}x{HEIGHT}"
    )
    shady.set_pipe_to(pipe_to = video_encoder)
    shady.render_to_video()
else:
    ffplay = interface.get_ffplay_wrapper()
    ffplay.configure(
        ffplay_binary_path = interface.find_binary("ffplay"),
        width = WIDTH,
        height = HEIGHT,
        pix_fmt = "rgba",  # rgba, rgb24, bgra
        framerate = FRAMERATE,
    )
    shady.set_pipe_to(pipe_to = ffplay)
    ffplay.start()
    shady.render_to_video()
    # shady.view_realtime()
