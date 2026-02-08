import gradio as gr


def hello(name):
    return f"Xin chào {name}!"


demo = gr.Interface(
    fn=hello,
    inputs="text",
    outputs="text",
    title="API Test",
    api_name="say_hello",  # <-- quan trọng nếu muốn custom endpoint
)

if __name__ == "__main__":
    demo.launch()
