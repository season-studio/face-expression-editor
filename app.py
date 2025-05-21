import gradio as gr
from PIL import Image
from urllib.parse import urlparse
import requests
import time
import os

from utils.gradio_helpers import parse_outputs, process_outputs

# Function to verify the image file type and resize it if necessary
def preprocess_image(image_path):
    # Check if the file exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"No such file: '{image_path}'")

    # Get the file extension and make sure it's a valid image format
    valid_extensions = ['jpg', 'jpeg', 'png', 'webp']
    file_extension = image_path.split('.')[-1].lower()

    if file_extension not in valid_extensions:
        raise ValueError("Invalid file type. Only JPG, PNG, and WEBP are allowed.")
    
    # Open the image
    with Image.open(image_path) as img:
        width, height = img.size

        # Check if any dimension exceeds 1024 pixels
        if width > 1024 or height > 1024:
            # Calculate the new size while maintaining aspect ratio
            if width > height:
                new_width = 1024
                new_height = int((new_width / width) * height)
            else:
                new_height = 1024
                new_width = int((new_height / height) * width)
            
            # Resize the image
            img_resized = img.resize((new_width, new_height), Image.LANCZOS)
            print(f"Resized image to {new_width}x{new_height}.")

            # Save the resized image as 'resized_image.jpg'
            output_path = 'resized_image.jpg'
            img_resized.save(output_path, 'JPEG')
            print(f"Resized image saved as {output_path}")
            return output_path
        else:
            print("Image size is within the limit, no resizing needed.")
            return image_path


def display_uploaded_image(image_in):
    return image_in

def reset_parameters():
    return gr.update(value=0), gr.update(value=0), gr.update(value=0), gr.update(value=0), gr.update(value=0), gr.update(value=0), gr.update(value=0), gr.update(value=0), gr.update(value=0), gr.update(value=0), gr.update(value=0), gr.update(value=0)

names = ['image', 'rotate_pitch', 'rotate_yaw', 'rotate_roll', 'blink', 'eyebrow', 'wink', 'pupil_x', 'pupil_y', 'aaa', 'eee', 'woo', 'smile', 'src_ratio', 'sample_ratio', 'crop_factor', 'output_format', 'output_quality']

def predict(request: gr.Request, *args, progress=gr.Progress(track_tqdm=True)):
    headers = {'Content-Type': 'application/json'}

    payload = {"input": {}}
    
    
    base_url = "http://0.0.0.0:7860"
    for i, key in enumerate(names):
        value = args[i]
        if value and (os.path.exists(str(value))):
            value = f"{base_url}/gradio_api/file=" + value
        if value is not None and value != "":
            payload["input"][key] = value

    time.sleep(0.5) 
    response = requests.post("http://0.0.0.0:5000/predictions", headers=headers, json=payload)
    
    
    if response.status_code == 201:
        time.sleep(0.5)
        follow_up_url = response.json()["urls"]["get"]
        response = requests.get(follow_up_url, headers=headers)
        while response.json()["status"] != "succeeded":
            if response.json()["status"] == "failed":
                raise gr.Error("The submission failed!")
            response = requests.get(follow_up_url, headers=headers)
            
    if response.status_code == 200:
        
        json_response = response.json()
        #If the output component is JSON return the entire output response 
        if(outputs[0].get_config()["name"] == "json"):
            return json_response["output"]
        predict_outputs = parse_outputs(json_response["output"])
        processed_outputs = process_outputs(predict_outputs)
        print(f"processed_outputs: {processed_outputs}")
        return tuple(processed_outputs) if len(processed_outputs) > 1 else processed_outputs[0]
    else:
        time.sleep(1)
        if(response.status_code == 409):
            raise gr.Error(f"Sorry, the Cog image is still processing. Try again in a bit.")
        raise gr.Error(f"The submission failed! Error: {response.status_code}")


css = '''
#col-container{max-width: 800px;margin: 0 auto;}
'''
with gr.Blocks(css=css) as demo:
    with gr.Column(elem_id="col-container"):
        gr.Markdown("# Expression Editor")
        gr.Markdown("Demo for expression-editor cog image by fofr")
        with gr.Row():
            with gr.Column():
                image = gr.Image(
                    label="Input image",
                    sources=["upload"],
                    type="filepath"
                )
                with gr.Tab("HEAD"):
                    with gr.Column():
                        rotate_pitch = gr.Slider(
                            label="Rotate Up-Down",
                            value=0,
                            minimum=-20, maximum=20
                        )
                        rotate_yaw = gr.Slider(
                            label="Rotate Left-Right turn", 
                            value=0,
                            minimum=-20, maximum=20
                        )
                        rotate_roll = gr.Slider(
                            label="Rotate Left-Right tilt", value=0,
                            minimum=-20, maximum=20
                        )
                with gr.Tab("EYES"):
                    with gr.Column():
                        eyebrow = gr.Slider(
                            label="Eyebrow", value=0,
                            minimum=-10, maximum=15
                        )
                        with gr.Row():
                            blink = gr.Slider(
                                label="Blink", value=0,
                                minimum=-20, maximum=5
                            )
                            
                            wink = gr.Slider(
                                label="Wink", value=0,
                                minimum=0, maximum=25
                            )
                        with gr.Row():
                            pupil_x = gr.Slider(
                                label="Pupil X", value=0,
                                minimum=-15, maximum=15
                            )
                            pupil_y = gr.Slider(
                                label="Pupil Y", value=0,
                                minimum=-15, maximum=15
                            )
                with gr.Tab("MOUTH"):
                    with gr.Column():
                        with gr.Row():
                            aaa = gr.Slider(
                                label="Aaa", value=0,
                                minimum=-30, maximum=120
                            )
                            eee = gr.Slider(
                                label="Eee", value=0,
                                minimum=-20, maximum=15
                            )
                            woo = gr.Slider(
                                label="Woo", value=0,
                                minimum=-20, maximum=15
                            )
                        smile = gr.Slider(
                            label="Smile", value=0,
                            minimum=-0.3, maximum=1.3
                        )
                with gr.Tab("More Settings"):
                    with gr.Column():
                        src_ratio = gr.Number(
                            label="Src Ratio", info='''Source ratio''', value=1
                        )
                        sample_ratio = gr.Slider(
                            label="Sample Ratio", info='''Sample ratio''', value=1,
                            minimum=-0.2, maximum=1.2
                        )
                        crop_factor = gr.Slider(
                            label="Crop Factor", info='''Crop factor''', value=1.7,
                            minimum=1.5, maximum=2.5
                        )
                        output_format = gr.Dropdown(
                            choices=['webp', 'jpg', 'png'], label="output_format", info='''Format of the output images''', value="webp"
                        )
                        output_quality = gr.Number(
                            label="Output Quality", info='''Quality of the output images, from 0 to 100. 100 is best quality, 0 is lowest quality.''', value=95
                        )
                with gr.Row():
                    reset_btn = gr.Button("Reset")
                    submit_btn = gr.Button("Submit")
            with gr.Column():
                result_image = gr.Image(elem_id="top")
                gr.HTML("""
                <div style="display: flex; flex-direction: column;justify-content: center; align-items: center; text-align: center;">
                    <p style="display: flex;gap: 6px;">
                         <a href="https://huggingface.co/spaces/fffiloni/expression-editor?duplicate=true">
                            <img src="https://huggingface.co/datasets/huggingface/badges/resolve/main/duplicate-this-space-lg.svg" alt="Duplicate this Space">
                        </a>
                    </p>
                    <p>to skip the queue and enjoy faster inference on the GPU of your choice </p>
                </div>
                """)

    inputs = [image, rotate_pitch, rotate_yaw, rotate_roll, blink, eyebrow, wink, pupil_x, pupil_y, aaa, eee, woo, smile, src_ratio, sample_ratio, crop_factor, output_format, output_quality]
    outputs = [result_image]

    image.upload(
        fn = preprocess_image,
        inputs = [image],
        outputs = [image],
        queue = False
    )

    reset_btn.click(
        fn = reset_parameters,
        inputs = None,
        outputs = [rotate_pitch, rotate_yaw, rotate_roll, blink, eyebrow, wink, pupil_x, pupil_y, aaa, eee, woo, smile],
        queue = False
    ).then(
        fn=predict,
        inputs=inputs,
        outputs=outputs,
        show_api=False
    )
    
    submit_btn.click(
        fn=predict,
        inputs=inputs,
        outputs=outputs,
        show_api=False
    )

    rotate_pitch.release(fn=predict, inputs=inputs, outputs=outputs, show_progress="minimal", show_api=False)
    rotate_yaw.release(fn=predict, inputs=inputs, outputs=outputs, show_progress="minimal", show_api=False)
    rotate_roll.release(fn=predict, inputs=inputs, outputs=outputs, show_progress="minimal", show_api=False)
    blink.release(fn=predict, inputs=inputs, outputs=outputs, show_progress="minimal", show_api=False)
    eyebrow.release(fn=predict, inputs=inputs, outputs=outputs, show_progress="minimal", show_api=False)
    wink.release(fn=predict, inputs=inputs, outputs=outputs, show_progress="minimal", show_api=False)
    pupil_x.release(fn=predict, inputs=inputs, outputs=outputs, show_progress="minimal", show_api=False)
    pupil_y.release(fn=predict, inputs=inputs, outputs=outputs, show_progress="minimal", show_api=False)
    aaa.release(fn=predict, inputs=inputs, outputs=outputs, show_progress="minimal", show_api=False)
    eee.release(fn=predict, inputs=inputs, outputs=outputs, show_progress="minimal", show_api=False)
    woo.release(fn=predict, inputs=inputs, outputs=outputs, show_progress="minimal", show_api=False)
    smile.release(fn=predict, inputs=inputs, outputs=outputs, show_progress="minimal", show_api=False)

demo.queue(api_open=False).launch(share=False, show_error=True, show_api=False)