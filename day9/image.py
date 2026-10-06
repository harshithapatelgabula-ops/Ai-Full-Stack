from diffusers import StableDiffusionPipeline
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5"
).to("cpu")
prompt = "Sunset in a futuristic city."
image = pipe(prompt,num_inference_steps=8).images[0]
image.show()