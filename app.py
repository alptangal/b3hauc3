# Cách ngắn nhất để có API
import gradio as gr


def xuly(text: str) -> str:
    return text.upper() + "!!!"


gr.Interface(
    fn=xuly,
    inputs="text",
    outputs="text",
    api_name="uppercase",  # ← endpoint /uppercase
).launch(server_name="0.0.0.0", server_port=8000)
