import gradio as gr
from shared.utils.plugins import WAN2GPPlugin
import json

class ConfigTabPlugin(WAN2GPPlugin):
    def __init__(self):
        super().__init__()
        self.name = "Configuration Tab"
        self.version = "1.1.0"
        self.description = "Lets you adjust all your performance and UI options for WAN2GP"

    def setup_ui(self):
        self.request_global("args")
        self.request_global("server_config")
        self.request_global("server_config_filename")
        self.request_global("attention_mode")
        self.request_global("compile")
        self.request_global("default_profile")
        self.request_global("vae_config")
        self.request_global("boost")
        self.request_global("preload_model_policy")
        self.request_global("transformer_quantization")
        self.request_global("transformer_dtype_policy")
        self.request_global("transformer_types")
        self.request_global("text_encoder_quantization")
        self.request_global("attention_modes_installed")
        self.request_global("attention_modes_supported")
        self.request_global("displayed_model_types")
        self.request_global("memory_profile_choices")
        self.request_global("save_path")
        self.request_global("image_save_path")
        self.request_global("quit_application")
        self.request_global("release_model")
        self.request_global("get_sorted_dropdown")
        self.request_global("app")
        self.request_global("fl")

        self.request_component("state")
        self.request_component("resolution")

        self.add_tab(
            tab_id="configuration",
            label="Configuration",
            component_constructor=self.create_config_ui,
            position=4
        )

    def create_config_ui(self):
        gr.Markdown("Please click 'Save' or 'Save and Restart' for changes to take effect. Some choices may be locked if set via command-line arguments.")
        with gr.Column():
            with gr.Tabs():
                with gr.Tab("General"):
                    _, _, dropdown_choices = self.get_sorted_dropdown(self.displayed_model_types, None, None, False)

                    self.transformer_types_choices = gr.Dropdown(
                        choices=dropdown_choices, value=self.transformer_types,
                        label="Selectable Generative Models (leave empty for all)", multiselect=True
                    )
                    self.model_hierarchy_type_choice = gr.Dropdown(
                        choices=[
                            ("Two Levels: Model Family > Models & Finetunes", 0),
                            ("Three Levels: Model Family > Models > Finetunes", 1),
                        ],
                        value=self.server_config.get("model_hierarchy_type", 1),
                        label="Models Hierarchy In User Interface",
                        visible=self.args.betatest if hasattr(self.args, 'betatest') else False,
                        interactive=not self.args.lock_config
                    )
                    self.fit_canvas_choice = gr.Dropdown(
                        choices=[
                            ("Dimensions are Pixel Budget (preserves aspect ratio, may exceed dimensions)", 0),
                            ("Dimensions are Max Width/Height (preserves aspect ratio, fits within box)", 1),
                            ("Dimensions are Exact Output (crops input to fit exact dimensions)", 2),
                        ],
                        value=self.server_config.get("fit_canvas", 0),
                        label="Input Image/Video Sizing Behavior",
                        interactive=not self.args.lock_config
                    )

                    def check_attn(mode):
                        if mode not in self.attention_modes_installed: return " (NOT INSTALLED)"
                        if mode not in self.attention_modes_supported: return " (NOT SUPPORTED)"
                        return ""

                    self.attention_choice = gr.Dropdown(
                        choices=[
                            ("Auto: Best available (sage2 > sage > sdpa)", "auto"),
                            ("sdpa: Default, always available", "sdpa"),
                            (f'flash{check_attn("flash")}: High quality, requires manual install', "flash"),
                            (f'xformers{check_attn("xformers")}: Good quality, less VRAM, requires manual install', "xformers"),
                            (f'sage{check_attn("sage")}: ~30% faster, requires manual install', "sage"),
                            (f'sage2{check_attn("sage2")}: ~40% faster, requires manual install', "sage2"),
                        ],
                        value=self.attention_mode, label="Attention Type", interactive=not self.args.lock_config
                    )
                    self.preload_model_policy_choice = gr.CheckboxGroup(
                        [("Preload Model on App Launch","P"), ("Preload Model on Switch", "S"), ("Unload Model when Queue is Done", "U")],
                        value=self.preload_model_policy, label="Model Loading/Unloading Policy"
                    )
                    self.clear_file_list_choice = gr.Dropdown(
                        choices=[("None", 0), ("Keep last video", 1), ("Keep last 5 videos", 5), ("Keep last 10", 10), ("Keep last 20", 20), ("Keep last 30", 30)],
                        value=self.server_config.get("clear_file_list", 5), label="Keep Previous Generations in Gallery"
                    )
                    self.display_stats_choice = gr.Dropdown(
                        choices=[("Disabled", 0), ("Enabled", 1)],
                        value=self.server_config.get("display_stats", 0), label="Display real-time RAM/VRAM stats (requires restart)"
                    )
                    self.max_frames_multiplier_choice = gr.Dropdown(
                        choices=[("Default", 1), ("x2", 2), ("x3", 3), ("x4", 4), ("x5", 5), ("x6", 6), ("x7", 7)],
                        value=self.server_config.get("max_frames_multiplier", 1), label="Max Frames Multiplier (requires restart)"
                    )
                    default_paths = self.fl.default_checkpoints_paths
                    checkpoints_paths_text = "\n".join(self.server_config.get("checkpoints_paths", default_paths))
                    self.checkpoints_paths_choice = gr.Textbox(
                        label="Model Checkpoint Folders (One Path per Line. First is Default Download Path)",
                        value=checkpoints_paths_text,
                        lines=3,
                        interactive=not self.args.lock_config
                    )
                    self.UI_theme_choice = gr.Dropdown(
                        choices=[("Blue Sky (Default)", "default"), ("Classic Gradio", "gradio")],
                        value=self.server_config.get("UI_theme", "default"), label="UI Theme (requires restart)"
                    )
                    self.queue_color_scheme_choice = gr.Dropdown(
                        choices=[
                            ("Pastel (Unique color for each item)", "pastel"),
                            ("Alternating Grey Shades", "alternating_grey"),
                        ],
                        value=self.server_config.get("queue_color_scheme", "pastel"),
                        label="Queue Color Scheme"
                    )

                with gr.Tab("Performance"):
                    self.quantization_choice = gr.Dropdown(choices=[("Scaled Int8 (recommended)", "int8"), ("16-bit (no quantization)", "bf16")], value=self.transformer_quantization, label="Transformer Model Quantization (if available)")
                    self.transformer_dtype_policy_choice = gr.Dropdown(choices=[("Auto (Best for Hardware)", ""), ("FP16", "fp16"), ("BF16", "bf16")], value=self.transformer_dtype_policy, label="Transformer Data Type (if available)")
                    self.mixed_precision_choice = gr.Dropdown(choices=[("16-bit only (less VRAM)", "0"), ("Mixed 16/32-bit (better quality)", "1")], value=self.server_config.get("mixed_precision", "0"), label="Transformer Engine Precision")
                    self.text_encoder_quantization_choice = gr.Dropdown(choices=[("16-bit (more RAM, better quality)", "bf16"), ("8-bit (less RAM, slightly lower quality)", "int8")], value=self.text_encoder_quantization, label="Text Encoder Precision")
                    self.VAE_precision_choice = gr.Dropdown(choices=[("16-bit (faster, less VRAM)", "16"), ("32-bit (slower, better for sliding window)", "32")], value=self.server_config.get("vae_precision", "16"), label="VAE Encoding/Decoding Precision")
                    self.compile_choice = gr.Dropdown(choices=[("On (up to 20% faster, requires Triton)", "transformer"), ("Off", "")], value=self.compile, label="Compile Transformer Model", interactive=not self.args.lock_config)
                    self.depth_anything_v2_variant_choice = gr.Dropdown(choices=[("Large (more precise, slower)", "vitl"), ("Big (less precise, faster)", "vitb")], value=self.server_config.get("depth_anything_v2_variant", "vitl"), label="Depth Anything v2 VACE Preprocessor")
                    self.vae_config_choice = gr.Dropdown(choices=[("Auto", 0), ("Disabled (fastest, high VRAM)", 1), ("256x256 Tiles (for >=8GB VRAM)", 2), ("128x128 Tiles (for >=6GB VRAM)", 3)], value=self.vae_config, label="VAE Tiling (to reduce VRAM usage)")
                    self.boost_choice = gr.Dropdown(choices=[("ON", 1), ("OFF", 2)], value=self.boost, label="Boost (~10% speedup for ~1GB VRAM)")
                    self.profile_choice = gr.Dropdown(choices=self.memory_profile_choices, value=self.default_profile, label="Memory Profile (Advanced)")
                    self.preload_in_VRAM_choice = gr.Slider(0, 40000, value=self.server_config.get("preload_in_VRAM", 0), step=100, label="VRAM (MB) for Preloaded Models (0=profile default)")
                    self.release_RAM_btn = gr.Button("Force Unload Models from RAM")

                with gr.Tab("Extensions"):
                    self.enhancer_enabled_choice = gr.Dropdown(choices=[("Off", 0), ("Florence 2 + LLama 3.2", 1), ("Florence 2 + Llama Joy (uncensored)", 2)], value=self.server_config.get("enhancer_enabled", 0), label="Prompt Enhancer (requires 8-14GB extra download)")
                    self.enhancer_mode_choice = gr.Dropdown(choices=[("Automatic on Generation", 0), ("On-Demand Button Only", 1)], value=self.server_config.get("enhancer_mode", 0), label="Prompt Enhancer Usage")
                    self.mmaudio_enabled_choice = gr.Dropdown(choices=[("Off", 0), ("Enabled (unloads after use)", 1), ("Enabled (persistent in RAM)", 2)], value=self.server_config.get("mmaudio_enabled", 0), label="MMAudio Soundtrack Generation (requires 10GB extra download)")

                with gr.Tab("Outputs"):
                    self.video_output_codec_choice = gr.Dropdown(choices=[("x265 CRF 28 (Balanced)", 'libx265_28'), ("x264 Level 8 (Balanced)", 'libx264_8'), ("x265 CRF 8 (High Quality)", 'libx265_8'), ("x264 Level 10 (High Quality)", 'libx264_10'), ("x264 Lossless", 'libx264_lossless')], value=self.server_config.get("video_output_codec", "libx264_8"), label="Video Codec")
                    self.image_output_codec_choice = gr.Dropdown(choices=[("JPEG Q85", 'jpeg_85'), ("WEBP Q85", 'webp_85'), ("JPEG Q95", 'jpeg_95'), ("WEBP Q95", 'webp_95'), ("WEBP Lossless", 'webp_lossless'), ("PNG Lossless", 'png')], value=self.server_config.get("image_output_codec", "jpeg_95"), label="Image Codec")
                    self.audio_output_codec_choice = gr.Dropdown(choices=[("AAC 128 kbit", 'aac_128')], value=self.server_config.get("audio_output_codec", "aac_128"), visible=False, label="Audio Codec to use")
                    self.metadata_choice = gr.Dropdown(
                        choices=[("Export JSON files", "json"), ("Embed metadata in file (Exif/tag)", "metadata"), ("None", "none")],
                        value=self.server_config.get("metadata_type", "metadata"), label="Metadata Handling"
                    )
                    self.embed_source_images_choice = gr.Checkbox(
                        value=self.server_config.get("embed_source_images", False),
                        label="Embed Source Images",
                        info="Saves i2v source images inside MP4 files"
                    )
                    self.video_save_path_choice = gr.Textbox(label="Video Output Folder (requires restart)", value=self.save_path)
                    self.image_save_path_choice = gr.Textbox(label="Image Output Folder (requires restart)", value=self.image_save_path)

                with gr.Tab("Notifications"):
                    self.notification_sound_enabled_choice = gr.Dropdown(choices=[("On", 1), ("Off", 0)], value=self.server_config.get("notification_sound_enabled", 0), label="Notification Sound")
                    self.notification_sound_volume_choice = gr.Slider(0, 100, value=self.server_config.get("notification_sound_volume", 50), step=5, label="Notification Volume")

            self.msg = gr.Markdown()
            with gr.Row():
                self.apply_btn = gr.Button("Save Settings")
                self.apply_and_restart_btn = gr.Button("Save and Restart", variant="primary")
        return [self.release_RAM_btn]

    def _save_changes(self, state, *args):
        if self.args.lock_config:
            return "<div style='color:red; text-align:center;'>Configuration is locked by command-line arguments.</div>"
        
        (
            transformer_types_choices, model_hierarchy_type_choice, fit_canvas_choice,
            attention_choice, preload_model_policy_choice, clear_file_list_choice,
            display_stats_choice, max_frames_multiplier_choice, checkpoints_paths_choice,
            UI_theme_choice, queue_color_scheme_choice,
            quantization_choice, transformer_dtype_policy_choice, mixed_precision_choice,
            text_encoder_quantization_choice, VAE_precision_choice, compile_choice,
            depth_anything_v2_variant_choice, vae_config_choice, boost_choice,
            profile_choice, preload_in_VRAM_choice,
            enhancer_enabled_choice, enhancer_mode_choice, mmaudio_enabled_choice,
            video_output_codec_choice, image_output_codec_choice, audio_output_codec_choice,
            metadata_choice, embed_source_images_choice,
            save_path_choice, image_save_path_choice,
            notification_sound_enabled_choice, notification_sound_volume_choice,
            last_resolution_choice
        ) = args

        if len(checkpoints_paths_choice.strip()) == 0:
            checkpoints_paths = self.fl.default_checkpoints_paths
        else:
            checkpoints_paths = checkpoints_paths_choice.replace("\r", "").split("\n")
            checkpoints_paths = [path.strip() for path in checkpoints_paths if len(path.strip()) > 0]

        self.fl.set_checkpoints_paths(checkpoints_paths)

        new_server_config = {
            "attention_mode": attention_choice, "transformer_types": transformer_types_choices,
            "text_encoder_quantization": text_encoder_quantization_choice, "save_path": save_path_choice,
            "image_save_path": image_save_path_choice, "compile": compile_choice, "profile": profile_choice,
            "vae_config": vae_config_choice, "vae_precision": VAE_precision_choice,
            "mixed_precision": mixed_precision_choice, "metadata_type": metadata_choice,
            "transformer_quantization": quantization_choice, "transformer_dtype_policy": transformer_dtype_policy_choice,
            "boost": boost_choice, "clear_file_list": clear_file_list_choice,
            "preload_model_policy": preload_model_policy_choice, "UI_theme": UI_theme_choice,
            "fit_canvas": fit_canvas_choice, "enhancer_enabled": enhancer_enabled_choice,
            "enhancer_mode": enhancer_mode_choice, "mmaudio_enabled": mmaudio_enabled_choice,
            "preload_in_VRAM": preload_in_VRAM_choice, "depth_anything_v2_variant": depth_anything_v2_variant_choice,
            "notification_sound_enabled": notification_sound_enabled_choice,
            "notification_sound_volume": notification_sound_volume_choice,
            "max_frames_multiplier": max_frames_multiplier_choice, "display_stats": display_stats_choice,
            "video_output_codec": video_output_codec_choice, "image_output_codec": image_output_codec_choice,
            "audio_output_codec": audio_output_codec_choice,
            "model_hierarchy_type": model_hierarchy_type_choice,
            "checkpoints_paths": checkpoints_paths,
            "queue_color_scheme": queue_color_scheme_choice,
            "embed_source_images": embed_source_images_choice,
            "last_model_type": state["model_type"],
            "last_model_per_family": state["last_model_per_family"],
            "last_model_per_type": state["last_model_per_type"],
            "last_advanced_choice": state["advanced"], "last_resolution_choice": last_resolution_choice,
            "last_resolution_per_group": state["last_resolution_per_group"],
        }
        
        if "enabled_plugins" in self.server_config:
            new_server_config["enabled_plugins"] = self.server_config["enabled_plugins"]

        if self.args.lock_config:
            if "attention_mode" in self.server_config: new_server_config["attention_mode"] = self.server_config["attention_mode"]
            if "compile" in self.server_config: new_server_config["compile"] = self.server_config["compile"]

        with open(self.server_config_filename, "w", encoding="utf-8") as writer:
            writer.write(json.dumps(new_server_config, indent=4))
        
        self.server_config.update(new_server_config)

        return "<div style='color:green; text-align:center;'>Settings saved. Please restart the application for all changes to take effect.</div>"

    def _save_and_restart(self, *args):
        self._save_changes(*args)
        gr.Info("Settings saved. Restarting application...")
        self.quit_application()

    def post_ui_setup(self, components: dict):
        state = components['state']
        resolution = components['resolution']

        inputs = [
            state,
            self.transformer_types_choices, self.model_hierarchy_type_choice, self.fit_canvas_choice,
            self.attention_choice, self.preload_model_policy_choice, self.clear_file_list_choice,
            self.display_stats_choice, self.max_frames_multiplier_choice, self.checkpoints_paths_choice,
            self.UI_theme_choice, self.queue_color_scheme_choice,
            self.quantization_choice, self.transformer_dtype_policy_choice, self.mixed_precision_choice,
            self.text_encoder_quantization_choice, self.VAE_precision_choice, self.compile_choice,
            self.depth_anything_v2_variant_choice, self.vae_config_choice, self.boost_choice,
            self.profile_choice, self.preload_in_VRAM_choice,
            self.enhancer_enabled_choice, self.enhancer_mode_choice, self.mmaudio_enabled_choice,
            self.video_output_codec_choice, self.image_output_codec_choice, self.audio_output_codec_choice,
            self.metadata_choice, self.embed_source_images_choice,
            self.video_save_path_choice, self.image_save_path_choice,
            self.notification_sound_enabled_choice, self.notification_sound_volume_choice,
            resolution
        ]

        self.apply_btn.click(
            fn=self._save_changes,
            inputs=inputs,
            outputs=[self.msg]
        )
        
        self.apply_and_restart_btn.click(
            fn=self._save_and_restart,
            inputs=inputs,
            outputs=None
        )

        def release_ram_and_notify():
            self.release_model()
            gr.Info("Models unloaded from RAM.")
        
        self.release_RAM_btn.click(fn=release_ram_and_notify)
        return {}