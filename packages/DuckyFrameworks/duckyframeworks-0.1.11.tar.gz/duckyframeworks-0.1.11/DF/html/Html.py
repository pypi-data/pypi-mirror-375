class DuckyHtml:
    def __init__(self, titulo=""):
        self.titulo = titulo
        self.content = []  # cada elemento será una tupla (nivel, línea)
        self.level = 0     # nivel actual de indentación
        self.crear_tags(['h1', 'h2', 'h3', 'p', 'h4', 'h5', 'h6'])

    def crear_tags(self, tags):
        for tag in tags:
            # cada lambda agrega línea con el nivel actual
            setattr(self, tag, lambda texto, id='', clase='', t=tag: self.content.append((self.level, f"""<{t} id="{id}" class="{clase}">{texto}</{t}>""")))
            
    def a(self, texto, href="#"):
        self.content.append((self.level, f'<a href="{href}">{texto}</a>'))

    def img(self, src, alt="", width=None, height=None):
        attrs = f'src="{src}" alt="{alt}"'
        if width:
            attrs += f' width="{width}"'
        if height:
            attrs += f' height="{height}"'
        self.content.append((self.level, f'<img {attrs}>'))
        
    def button(self, texto, type="button", id="", clase=""):
        self.content.append((self.level, f'<button type="{type}" id="{id}" class="{clase}">{texto}</button>'))

    # Métodos para abrir y cerrar contenedores si quieres (div, section, etc.)
    def open_tag(self, tag):
        self.content.append((self.level, f"<{tag}>"))
        self.level += 1  # subimos nivel

    def close_tag(self, tag):
        self.level -= 1  # bajamos nivel
        self.content.append((self.level, f"</{tag}>"))

    def code(self):
        lines = []
        for lvl, line in self.content:
            lines.append("    " * lvl + line)  # 4 espacios por nivel
        body_content = "\n".join(lines)
        return f"""<!DOCTYPE html>
<html>
    <head>
        <title>{self.titulo}</title>
    </head>
    <body>
{body_content}
    </body>
</html>"""
