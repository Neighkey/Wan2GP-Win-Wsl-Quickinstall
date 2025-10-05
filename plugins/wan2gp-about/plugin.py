import gradio as gr
from shared.utils.plugins import WAN2GPPlugin

class AboutPlugin(WAN2GPPlugin):
    def __init__(self):
        super().__init__()
        self.name = "About Tab"
        self.version = "1.0.0"

    def setup_ui(self):
        self.add_tab(
            tab_id="about_tab",
            label="About",
            component_constructor=self.create_about_ui
        )

    def create_about_ui(self):
        gr.Markdown("<H2>WanGP - AI Generative Models for the GPU Poor by <B>DeepBeepMeep</B> (<A HREF='https://github.com/deepbeepmeep/Wan2GP'>GitHub</A>)</H2>")
        gr.Markdown("Many thanks to:")
        gr.Markdown("- <B>Alibaba Wan Team</B> for the best open source video generators (https://github.com/Wan-Video/Wan2.1)")
        gr.Markdown("- <B>Alibaba Vace, Multitalk and Fun Teams</B> for their incredible control net models (https://github.com/ali-vilab/VACE), (https://github.com/MeiGen-AI/MultiTalk) and  (https://huggingface.co/alibaba-pai/Wan2.2-Fun-A14B-InP) ")
        gr.Markdown("- <B>Tencent</B> for the impressive Hunyuan Video models (https://github.com/Tencent-Hunyuan/HunyuanVideo)")
        gr.Markdown("- <B>Blackforest Labs</B> for the innovative Flux image generators (https://github.com/black-forest-labs/flux)")
        gr.Markdown("- <B>Alibaba Qwen Team</B> for their state of the art Qwen Image generators (https://github.com/QwenLM/Qwen-Image)")
        gr.Markdown("- <B>Lightricks</B> for their super fast LTX Video models (https://github.com/Lightricks/LTX-Video)")
        gr.Markdown("- <B>Hugging Face</B> for providing hosting for the models and developing must have open source libraries such as Tranformers, Diffusers, Accelerate and Gradio (https://huggingface.co/)")
        gr.Markdown("<BR>Huge acknowledgments to these great open source projects used in WanGP:")
        gr.Markdown("- <B>Rife</B>: temporal upsampler (https://github.com/hzwer/ECCV2022-RIFE)")
        gr.Markdown("- <B>DwPose</B>: Open Pose extractor (https://github.com/IDEA-Research/DWPose)")
        gr.Markdown("- <B>DepthAnything</B> & <B>Midas</B>: Depth extractors (https://github.com/DepthAnything/Depth-Anything-V2) and (https://github.com/isl-org/MiDaS")
        gr.Markdown("- <B>Matanyone</B> and <B>SAM2</B>: Mask Generation (https://github.com/pq-yang/MatAnyone) and (https://github.com/facebookresearch/sam2)")
        gr.Markdown("- <B>Pyannote</B>: speaker diarization (https://github.com/pyannote/pyannote-audio)")

        gr.Markdown("<BR>Special thanks to the following people for their support:")
        gr.Markdown("- <B>Cocktail Peanuts</B> : QA dpand simple installation via Pinokio.computer")
        gr.Markdown("- <B>Tophness</B> : created (former) multi tabs and queuing frameworks")
        gr.Markdown("- <B>AmericanPresidentJimmyCarter</B> : added original support for Skip Layer Guidance")
        gr.Markdown("- <B>Remade_AI</B> : for their awesome Loras collection")
        gr.Markdown("- <B>Reevoy24</B> : for his repackaging / completing the documentation")
        gr.Markdown("- <B>Redtash1</B> : for designing the protype of the RAM / VRAM stats viewer")