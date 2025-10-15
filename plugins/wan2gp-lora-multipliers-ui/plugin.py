import gradio as gr
from shared.utils.plugins import WAN2GPPlugin
import time

class LoraMultipliersUIPlugin(WAN2GPPlugin):
    def __init__(self):
        super().__init__()
        self.name = "Lora Multipliers UI"
        self.version = "1.0.0"
        self.description = "Dynamically set lora multipliers with slider bars instead of text"
        self.request_component("loras_multipliers")
        self.request_component("loras_choices")
        self.request_component("guidance_phases")
        self.request_component("num_inference_steps")
        self.request_component("main")

    def post_ui_setup(self, components: dict) -> dict:
        loras_multipliers = self.loras_multipliers
        loras_choices = self.loras_choices
        guidance_phases = self.guidance_phases
        num_inference_steps = self.num_inference_steps
        main_ui_block = self.main

        def create_and_wire_ui():
            MAX_LORA_SLIDERS = 15
            MAX_STEP_SPLITS = 5

            css = """
            <style>
                #lora_builder_main_group {
                    font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
                }
                .lora-main-container {
                    border: 1px solid var(--border-color-primary);
                    border-radius: 8px;
                    padding: 12px;
                    margin-bottom: 0px !important;
                    background-color: var(--background-fill-secondary);
                }
                .lora-main-container > .gr-row {
                    margin-bottom: 8px;
                    justify-content: space-between;
                    align-items: center;
                }
                .lora-step-split-container {
                    border: 1px dashed var(--border-color-accent);
                    border-radius: 6px;
                    padding: 10px;
                    margin-top: 8px;
                }
                .lora-main-container button {
                    padding: 4px 12px !important;
                    font-size: 1em !important;
                    min-width: fit-content !important;
                    flex-grow: 0;
                    background: var(--button-secondary-background-fill);
                    color: var(--button-secondary-text-color);
                    border: 1px solid var(--button-secondary-border-color);
                }
                .lora-main-container button:hover {
                    background: var(--button-secondary-background-fill-hover);
                    border-color: var(--button-secondary-border-color-hover);
                }
                .lora-step-split-container > .gr-row {
                    gap: 16px;
                    align-items: end; 
                }
                .lora-step-split-container .form {
                    flex-grow: 1;
                }
                .lora-section-header h3 {
                    border-bottom: 1px solid var(--border-color-primary);
                    padding-bottom: 4px;
                    margin-top: 16px;
                    margin-bottom: 0px;
                }
                #lora_builder_main_group > div:first-child > h3 {
                    margin-top: 0;
                }
            </style>
            """

            def _build_multipliers_string(num_selected_loras, guidance_phases_val, split_counts, all_slider_values_flat, separator_index=-1):
                textbox_strings = []
                slider_cursor = 0
                for i in range(MAX_LORA_SLIDERS):
                    if i < num_selected_loras:
                        num_splits_for_this_lora = split_counts[i]
                        lora_step_strings = []
                        for j in range(MAX_STEP_SPLITS):
                            phase_values_for_textbox = []
                            if j < num_splits_for_this_lora:
                                for k in range(3):
                                    is_visible = (k + 1) <= guidance_phases_val
                                    if is_visible:
                                        phase_value = all_slider_values_flat[slider_cursor + k]
                                        formatted_value = str(int(phase_value)) if phase_value == int(phase_value) else f"{phase_value:.2f}".rstrip('0').rstrip('.')
                                        phase_values_for_textbox.append(formatted_value)
                            
                            if phase_values_for_textbox:
                                lora_step_strings.append(";".join(phase_values_for_textbox))
                            slider_cursor += 3
                        
                        if lora_step_strings:
                            textbox_strings.append(",".join(lora_step_strings))
                    else:
                        slider_cursor += MAX_STEP_SPLITS * 3
                
                if not textbox_strings:
                    return ""

                if separator_index != -1 and num_selected_loras < separator_index:
                    separator_index = -1

                if separator_index > 0 and separator_index <= len(textbox_strings):
                    part1 = " ".join(textbox_strings[:separator_index])
                    part2 = " ".join(textbox_strings[separator_index:])
                    if part2:
                        return f"{part1}|{part2}"
                    else:
                        return f"{part1}|"
                else:
                    return " ".join(textbox_strings)

            def update_slider_ui_and_textbox(selected_lora_indices, guidance_phases_val, current_multipliers_str, total_steps, current_split_counts_state, split_lora_index=-1, rejoin_lora_index=-1):
                multipliers_per_lora = []
                separator_index = -1
                if current_multipliers_str:
                    if '|' in current_multipliers_str:
                        parts = current_multipliers_str.split('|')
                        loras_before_sep = [s for s in parts[0].split(' ') if s]
                        separator_index = len(loras_before_sep)
                    multipliers_per_lora = [s for s in current_multipliers_str.replace('|', ' ').split(' ') if s]

                new_split_counts = list(current_split_counts_state)

                if split_lora_index == -1 and rejoin_lora_index == -1:
                    for i in range(len(multipliers_per_lora)):
                        if i < MAX_LORA_SLIDERS:
                            num_splits = len(multipliers_per_lora[i].split(','))
                            new_split_counts[i] = max(1, num_splits)

                if split_lora_index != -1:
                    if new_split_counts[split_lora_index] < MAX_STEP_SPLITS:
                        new_split_counts[split_lora_index] += 1
                elif rejoin_lora_index != -1:
                    if new_split_counts[rejoin_lora_index] > 1:
                        new_split_counts[rejoin_lora_index] -= 1 # Decrement instead of resetting
                
                current_split_counts = new_split_counts
                
                ui_updates = {}
                all_slider_values_flat = []
                
                num_selected_loras = len(selected_lora_indices)
                has_separator = separator_index != -1
                show_accelerator_header = has_separator and separator_index > 0                
                ui_updates[accelerator_loras_header] = gr.update(visible=show_accelerator_header and num_selected_loras > 0)
                
                for i in range(MAX_LORA_SLIDERS):
                    group_data = lora_slider_ui_groups[i]
                    is_lora_visible = i < num_selected_loras
                    
                    is_first_user_lora = (i == 0 and not show_accelerator_header) or (i == separator_index)
                    show_user_header_here = is_first_user_lora and num_selected_loras > i
                    ui_updates[group_data["user_header"]] = gr.update(visible=show_user_header_here)
                    
                    ui_updates[group_data["main_group"]] = gr.update(visible=is_lora_visible)

                    if is_lora_visible:
                        lora_name = selected_lora_indices[i]
                        ui_updates[group_data["name"]] = gr.update(value=f"### {lora_name}")
                        
                        num_splits_for_this_lora = current_split_counts[i]
                        
                        ui_updates[group_data["split_button"]] = gr.update(visible=(num_splits_for_this_lora < MAX_STEP_SPLITS))
                        ui_updates[group_data["rejoin_button"]] = gr.update(visible=(num_splits_for_this_lora > 1))
                        
                        steps_and_phases_str = multipliers_per_lora[i] if i < len(multipliers_per_lora) else ""
                        multipliers_per_step = steps_and_phases_str.split(',')
                        
                        steps_per_split_base = total_steps
                        remainder = total_steps % num_splits_for_this_lora
                        start_step = 0
                        
                        for j in range(MAX_STEP_SPLITS):
                            split_data = group_data["splits"][j]
                            is_split_visible = j < num_splits_for_this_lora
                            ui_updates[split_data["group"]] = gr.update(visible=is_split_visible)

                            if is_split_visible:
                                steps_in_this_split = steps_per_split_base + (1 if j < remainder else 0)
                                end_step = start_step + steps_in_this_split
                                step_title = f"**Steps {start_step + 1} to {end_step}**"
                                start_step = end_step
                                ui_updates[split_data["title"]] = gr.update(value=step_title)
                                
                                multipliers_per_phase = multipliers_per_step[j].split(';') if j < len(multipliers_per_step) else ['1.0'] * 3
                                
                                for k in range(3):
                                    try: phase_value = float(multipliers_per_phase[k])
                                    except (ValueError, IndexError): phase_value = 1.0
                                    
                                    is_slider_visible = (k + 1) <= guidance_phases_val
                                    ui_updates[split_data["sliders"][k]] = gr.update(visible=is_slider_visible, value=phase_value)
                                    all_slider_values_flat.append(phase_value)
                            else:
                                all_slider_values_flat.extend([1.0] * 3)
                    else:
                        ui_updates[group_data["split_button"]] = gr.update(visible=False)
                        ui_updates[group_data["rejoin_button"]] = gr.update(visible=False)
                        all_slider_values_flat.extend([1.0] * 3 * MAX_STEP_SPLITS)

                effective_separator_index = separator_index
                if effective_separator_index != -1 and num_selected_loras < effective_separator_index:
                    effective_separator_index = -1

                new_textbox_value = _build_multipliers_string(num_selected_loras, guidance_phases_val, current_split_counts, all_slider_values_flat, effective_separator_index)
                return [effective_separator_index, current_split_counts, gr.update(value=new_textbox_value), ui_updates]

            def update_textbox_from_sliders(selected_loras, guidance_phases_val, split_counts, separator_index, *all_slider_values_flat):
                effective_separator_index = separator_index
                if effective_separator_index != -1 and len(selected_loras) < effective_separator_index:
                    effective_separator_index = -1
                new_textbox_value = _build_multipliers_string(len(selected_loras), guidance_phases_val, split_counts, all_slider_values_flat, effective_separator_index)
                return gr.update(value=new_textbox_value)

            with gr.Accordion("Dynamic Lora Multipliers Adjustments", open=True) as main_accordion:
                gr.HTML(value=css)
                lora_separator_index = gr.State(-1)
                lora_split_counts = gr.State([1] * MAX_LORA_SLIDERS)
                lora_slider_ui_groups = []

                update_mults_btn = gr.Button(visible=False, elem_id="lora_mults_update_btn")

                with gr.Group(elem_id="lora_builder_main_group"):
                    accelerator_loras_header = gr.Markdown("<h3>Accelerator LoRAs</h3>", visible=False, elem_classes="lora-section-header")
                    for i in range(MAX_LORA_SLIDERS):
                        user_loras_header = gr.Markdown("<h3>User LoRAs</h3>", visible=False, elem_classes="lora-section-header")
                        with gr.Column(visible=False, elem_classes="lora-main-container") as lora_main_group:
                            with gr.Row(variant="compact"):
                                lora_name_md = gr.Markdown()
                                with gr.Row():
                                    split_steps_btn = gr.Button("Split Steps")
                                    rejoin_steps_btn = gr.Button("Rejoin Step", visible=False)
                            
                            split_groups = []
                            for j in range(MAX_STEP_SPLITS):
                                with gr.Column(visible=False, elem_classes="lora-step-split-container") as lora_step_group:
                                    step_range_md = gr.Markdown()
                                    with gr.Row():
                                        phase1_slider = gr.Slider(minimum=0.0, maximum=1.0, value=1.0, step=0.05, label="Phase 1", interactive=True)
                                        phase2_slider = gr.Slider(minimum=0.0, maximum=1.0, value=1.0, step=0.05, label="Phase 2", interactive=True, visible=False)
                                        phase3_slider = gr.Slider(minimum=0.0, maximum=1.0, value=1.0, step=0.05, label="Phase 3", interactive=True, visible=False)
                                    split_groups.append({ "group": lora_step_group, "title": step_range_md, "sliders": [phase1_slider, phase2_slider, phase3_slider] })
                            
                            lora_slider_ui_groups.append({ 
                                "main_group": lora_main_group, 
                                "name": lora_name_md, 
                                "split_button": split_steps_btn, 
                                "rejoin_button": rejoin_steps_btn,
                                "splits": split_groups,
                                "user_header": user_loras_header
                            })

            slider_ui_outputs_flat = []
            all_sliders_flat = []
            slider_ui_outputs_flat.append(accelerator_loras_header)
            for group in lora_slider_ui_groups:
                slider_ui_outputs_flat.append(group["user_header"])
                slider_ui_outputs_flat.extend([group["main_group"], group["name"], group["split_button"], group["rejoin_button"]])
                for split in group["splits"]:
                    slider_ui_outputs_flat.extend([split["group"], split["title"], *split["sliders"]])
                    all_sliders_flat.extend(split["sliders"])

            def unpack_dict_updates_fn(*args, **kwargs):
                state_outs_and_dict = update_slider_ui_and_textbox(*args, **kwargs)
                states = state_outs_and_dict[:-1]
                updates_dict = state_outs_and_dict[-1]

                unpacked_list = []
                for component in slider_ui_outputs_flat:
                    unpacked_list.append(updates_dict.get(component, gr.update()))
                return states + unpacked_list

            events_to_trigger_ui_update = [loras_choices.change, guidance_phases.change, num_inference_steps.change, loras_multipliers.blur]
            for event in events_to_trigger_ui_update:
                event(
                    fn=unpack_dict_updates_fn,
                    inputs=[loras_choices, guidance_phases, loras_multipliers, num_inference_steps, lora_split_counts, gr.State(-1), gr.State(-1)],
                    outputs=[lora_separator_index, lora_split_counts, loras_multipliers] + slider_ui_outputs_flat,
                    show_progress="hidden"
                )

            for i, group in enumerate(lora_slider_ui_groups):
                group["split_button"].click(
                    fn=unpack_dict_updates_fn,
                    inputs=[loras_choices, guidance_phases, loras_multipliers, num_inference_steps, lora_split_counts, gr.State(i), gr.State(-1)],
                    outputs=[lora_separator_index, lora_split_counts, loras_multipliers] + slider_ui_outputs_flat,
                    show_progress="hidden"
                )
                group["rejoin_button"].click(
                    fn=unpack_dict_updates_fn,
                    inputs=[loras_choices, guidance_phases, loras_multipliers, num_inference_steps, lora_split_counts, gr.State(-1), gr.State(i)],
                    outputs=[lora_separator_index, lora_split_counts, loras_multipliers] + slider_ui_outputs_flat,
                    show_progress="hidden"
                )

            update_mults_btn.click(
                fn=update_textbox_from_sliders,
                inputs=[loras_choices, guidance_phases, lora_split_counts, lora_separator_index] + all_sliders_flat,
                outputs=[loras_multipliers],
                show_progress="hidden"
            )

            for slider in all_sliders_flat:
                slider.release(fn=None, js="""
                    () => {
                        if (!window.wgpLoraUIDebouncedUpdate) {
                            const debounce = (func, delay) => {
                                let timeout;
                                return (...args) => {
                                    clearTimeout(timeout);
                                    timeout = setTimeout(() => func.apply(this, args), delay);
                                };
                            };
                            window.wgpLoraUIDebouncedUpdate = debounce(() => {
                                const btn = document.getElementById('lora_mults_update_btn');
                                if (btn) btn.click();
                            }, 200);
                        }
                        window.wgpLoraUIDebouncedUpdate();
                    }
                """)

            main_ui_block.load(
                fn=unpack_dict_updates_fn,
                inputs=[loras_choices, guidance_phases, loras_multipliers, num_inference_steps, lora_split_counts, gr.State(-1), gr.State(-1)],
                outputs=[lora_separator_index, lora_split_counts, loras_multipliers] + slider_ui_outputs_flat,
                show_progress="hidden"
            )

            return main_accordion

        self.insert_after(
            target_component_id="loras_multipliers",
            new_component_constructor=create_and_wire_ui
        )
        
        return {
            loras_multipliers: gr.update(elem_id="loras_multipliers_textbox", interactive=True)
        }