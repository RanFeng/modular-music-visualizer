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
    t = 20,
    vflip = True,
    scale = f"{WIDTH}x{HEIGHT}"
)

# Set the encoder
shady.get_ffmpeg_wrapper(
    ffmpeg = video_encoder
)

sep = os.path.sep

# # Shader

shady_maker.empty_shader()
shader = shady_maker.write_current_shader()

shady_maker.add_mapping("background", "image", f"{interface.MMV_INTERFACE_ROOT}{sep}..{sep}..{sep}repo{sep}piano-roll.jpg")
shader = shady_maker.write_current_shader()

shady_maker.add_mapping("logo", "image",  f"{interface.MMV_INTERFACE_ROOT}{sep}..{sep}..{sep}repo{sep}mmv-project-logo.png")
shader = shady_maker.write_current_shader()


# Layer 1

shady_maker.add_layer(layer_number = 1)
shader = shady_maker.write_current_shader()

target = "background"
angle = "sin(iTime/2.2385)/50.0 + cos(iTime/3.49234)/60"
shift_decrease = 80.0
shift = f"vec2(sin(iTime*1.2353)/{shift_decrease}, sin(iTime*1.53489)/{shift_decrease} )"
scale = "1.2 + sin(iTime)/40 + cos(iTime*1.13515)/50"
repeat = "true"

shady_maker.add_layer_content(layer_number = 1,
    code = f"""\
    layercolor = mmv_blit_image(layercolor, {target}, {target}Size, uv, {shift}, vec2(0.5, 0.5), {scale}, {angle}, {repeat});"""
)
shader = shady_maker.write_current_shader()


# Layer 2

shady_maker.add_layer(layer_number = 2)
shader = shady_maker.write_current_shader()


target = "logo"
angle = "sin(iTime)/30.0 + cos(iTime*1.315135)/40"
shift_decrease = 80.0
shift = f"vec2(sin(iTime*1.2353)/{shift_decrease}, sin(iTime*1.53489)/{shift_decrease} )"
scale = "0.3 + sin(iTime*4.153)/200 + cos(iTime*2.13515)/300"
repeat = "false"

shady_maker.add_layer_content(layer_number = 2,
    code = f"""\
    layercolor = mmv_blit_image(layercolor, {target}, {target}Size, uv, {shift}, vec2(0.5, 0.5), {scale}, {angle}, {repeat});"""
)
shader = shady_maker.write_current_shader()





shady_maker.add_layer(layer_number = 3, alpha_composite = False)
shader = shady_maker.write_current_shader()

# Multi sampling
shady_maker.add_layer_content(layer_number = 3,
    code = f"""\
    vec2 lookup = 0.000002 * iResolution.xy;
    vec4 multisampled = vec4(0.0);
    float many = 40;
    float tau = 3.1415*2;

    for (float i = 0.0; i < tau; i += tau / many){{
        multisampled += PREV_LAYER(uv + vec2(sin(rand(i)), cos(rand(i+1))) * lookup);
    }}

    layercolor = multisampled / many;
""")




shady_maker.camera_transformation("uv *= atan(iTime); uv += vec2(3.1415/2.0 - atan(iTime*2.3123), 3.1415/2.0 - atan(iTime*3.0));")

# Output

shady_maker.hook_last_layer_to_output()
shader = shady_maker.write_current_shader()

# #

shady.base_configuration(
    shady_binary = interface.find_binary("shady"),
    width = int(WIDTH * supersampling),
    height = int(HEIGHT * supersampling),
    framerate = FRAMERATE,
    main_glsl = shader,
)

if "render" in sys.argv:
    shady.render_to_video()
else:
    shady.view_realtime()
