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
interface = mmv.MMVPackageInterface()

# Testing
# interface.check_download_externals(target_externals = ["ffmpeg", "mpv", "musescore"], platform = "windows")
# interface.check_download_externals(target_externals = ["ffmpeg", "mpv", "musescore", "golang", "shady", "upgrade-shady"])
interface.check_download_externals(target_externals = ["ffmpeg", "mpv", "musescore", "golang", "shady"])

# Shader interface >:)
mmv_shader_interface = interface.get_shader_interface()
shady = mmv_shader_interface.mmv_shader_main.shady

WIDTH = 1280
HEIGHT = 720
FRAMERATE = 60
supersampling = 1

sep = os.path.sep

global_shader = mmv_shader_interface.new_shady_shader()
global_shader.empty_shader(shader_type = "global")

# layer1 = mmv_shader_interface.new_shady_shader()
# layer1.empty_shader(shader_type = "layer")
# layer1.add_contents("col = vec4(uv.x, 0.0, 0.0, uv.x);")
# layer1.save()

layer2 = mmv_shader_interface.new_shady_shader()
layer2.empty_shader(shader_type = "layer")
layer2.add_mapping(name = "image", map_type = "image", path = f"{THIS_DIR}/../assets/tremx_assets/secret-image.png")

target = "image"
angle = "sin(iTime/2.2385)/50.0 + cos(iTime/3.49234)/60"
shift_decrease = 80.0
shift = f"vec2(sin(iTime*1.2353)/{shift_decrease}, sin(iTime*1.53489)/{shift_decrease} )"
scale = "1.5 + sin(iTime)/40 + cos(iTime*1.13515)/50"
repeat = "true"

layer2.add_function(
f"""\
vec4 draw_image(in vec4 canvas, in vec2 uv) {{
    return mmv_blit_image(canvas, {target}, {target}Size, uv, {shift}, vec2(0.5, 0.5), {scale}, {angle}, {repeat});
}}
""")

# Chromatic aberration on top of image
layer2.add_contents(
f"""\
//float amount = 0.003;
float amount = 0.003 + (iTime/10000);

vec4 col_r = draw_image(col, uv + (vec2(sin(iTime*2.31245), cos(iTime/2.123) + sin(iTime*3.12415)) * amount));
vec4 col_g = draw_image(col, uv + 3*(vec2(cos(iTime/2), cos(iTime/4.1234)) * amount));
vec4 col_b = draw_image(col, uv + 4*(vec2(cos(iTime/1.35135), sin(iTime*1.23)) * amount));

col.r = col_r.r;
col.g = col_g.g;
col.b = col_b.b;
"""
)

# # Simple image drawing
# layer2.add_contents(
#     f"col = mmv_blit_image(col, {target}, {target}Size, uv, {shift}, vec2(0.5, 0.5), {scale}, {angle}, {repeat});"
# )

# Zoom in effect on background
layer2.camera_transformation("uv = uv * atan(iTime);")
layer2.save()

# # Add layers

layers = [layer2]

for layer in layers:
    global_shader.add_alpha_composite_layer(shady_maker = layer, width = WIDTH, height = HEIGHT)

global_shader.save()


# #

shady.base_configuration(
    shady_binary = interface.find_binary("shady"),
    width = int(WIDTH * supersampling),
    height = int(HEIGHT * supersampling),
    framerate = FRAMERATE,
    main_glsl = global_shader.path,
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
        preset = "slow",
        hwaccel = "auto",
        loglevel = "",
        nostats = False,
        hide_banner = True,
        opencl = False,
        crf = 23,
        tune = "film",
        vcodec = "libx264",
        override = True,
        t = 50,
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
        vflip = True,
        framerate = FRAMERATE,
    )
    shady.set_pipe_to(pipe_to = ffplay)
    ffplay.start()
    shady.render_to_video()
    # shady.view_realtime()
