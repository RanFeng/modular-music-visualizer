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
shader_shady_maker = mmv_shader_interface.mmv_shader_main.shady_shader_maker

WIDTH = 1280
HEIGHT = 720
FRAMERATE = 60

# Video encoder
video_encoder = interface.get_ffmpeg_wrapper()
video_encoder.configure_encoding(
    ffmpeg_binary_path = interface.find_binary("ffmpeg"),
    width = WIDTH,
    height = HEIGHT,
    input_audio_source = None,
    input_video_source = "pipe",
    output_video = f"{THIS_DIR}/../mmvshady.mp4",
    pix_fmt = "rgba",
    framerate = FRAMERATE,
    preset = "slow",
    hwaccel = "auto",
    loglevel = "",
    nostats = False,
    hide_banner = True,
    opencl = False,
    crf = 17,
    tune = "film",
    vcodec = "libx264",
    override = True,
    t = 10,
    vflip = True,
)

# Set the encoder
shady.get_ffmpeg_wrapper(
    ffmpeg = video_encoder
)


# # Shader



# #

shady.base_configuration(
    shady_binary = interface.find_binary("shady"),
    width = WIDTH,
    height = HEIGHT,
    framerate = FRAMERATE,
    main_glsl = f"{mmv_shader_interface.MMV_SHADER_ROOT}/glsl/shady/sketch-template.glsl",
)

if "render" in sys.argv:
    shady.render_to_video()
else:
    shady.view_realtime()
