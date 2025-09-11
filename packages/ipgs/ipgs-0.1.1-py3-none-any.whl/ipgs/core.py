# ipgs/core.py

from IPython.display import display, HTML, Javascript, clear_output

class iPgs:
    def __init__(self, iterable, description="Progress", height_px=8, width_px=300):
        self.iterable = list(iterable)
        self.total = len(self.iterable)
        self.description = description
        self.height_px = height_px
        self.width_px = width_px
        self._render_bar()

    def _render_bar(self):
        clear_output(wait=True)
        html = f"""
        <style>
            .progress-wrapper {{
                width: {self.width_px}px;
                margin: 20px auto;
            }}
            .progress-container {{
                width: 100%;
                height: {self.height_px}px;
                background-color: #eee;
                border-radius: 4px;
                overflow: hidden;
                border: 1px solid #ccc;
            }}
            .progress-bar {{
                height: 100%;
                width: 0%;
                background: linear-gradient(270deg, #00c6ff, #0072ff, #00c6ff);
                background-size: 600% 100%;
                animation: gradientMove 2s linear infinite;
                transition: width 0.4s ease-in-out;
            }}
            .progress-bar:hover {{
                filter: brightness(130%);
                box-shadow: 0 0 5px rgba(0,0,0,0.2);
            }}
            @keyframes gradientMove {{
                0% {{ background-position: 100% 0; }}
                100% {{ background-position: -100% 0; }}
            }}
            #progress-text {{
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                margin-top: 6px;
                color: #333;
                text-align: center;
            }}
        </style>
        <div class="progress-wrapper">
            <div class="progress-container">
                <div class="progress-bar" id="fancyBar"></div>
            </div>
            <div id="progress-text">{self.description}</div>
        </div>
        """
        display(HTML(html))
        self.js_display = display(Javascript(""), display_id="progress_js")

    def __iter__(self):
        for i, item in enumerate(self.iterable):
            self._update(i)
            yield item

    def _update(self, step):
        progress = (step + 1) / self.total * 100
        if progress >= 100:
            js_code = """
            const bar = document.getElementById('fancyBar');
            if (bar) {
                bar.style.animation = 'none';
                bar.style.background = '#4CAF50';
                bar.style.width = '100%';
            }
            const text = document.getElementById('progress-text');
            if (text) {
                text.innerText = '✅ Training Complete';
            }
            """
        else:
            js_code = f"""
            const bar = document.getElementById('fancyBar');
            if (bar) {{
                bar.style.width = '{progress}%';
            }}
            const text = document.getElementById('progress-text');
            if (text) {{
                text.innerText = '{self.description}: Step {step + 1}/{self.total} - {progress:.1f}%';
            }}
            """
        self.js_display.update(Javascript(js_code))
