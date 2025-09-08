from pictex import *
from pathlib import Path

ASSETS_DIR = Path(__file__).parent / "tests" / "assets"
STATIC_FONT_PATH = str(ASSETS_DIR / "Lato-BoldItalic.ttf") # No emojies and japanese support
VARIABLE_WGHT_FONT_PATH = str(ASSETS_DIR / "Oswald-VariableFont_wght.ttf")
JAPANESE_FONT_PATH = str(ASSETS_DIR / "NotoSansJP-Regular.ttf")
IMAGE_PATH = str(ASSETS_DIR / "image.png")
LONG_TEXT = "This is a very long sentence that will demonstrate text wrapping behavior when placed inside containers with various width constraints and settings."
ONE_LONG_WORD = "OneLongWord"

# one_long_word = Column(Text(ONE_LONG_WORD).font_weight(700)).border(3, "blue")
# long_text = Column(Text(LONG_TEXT).font_weight(700)).border(3, "red")

# container = Row(
#     one_long_word,
#     long_text
# ).padding(20).background_color("white").border_radius(10).size(width=700)

# canvas = Canvas().background_color("#DAE0E6").padding(40)

# parent = Row(
#     Image(IMAGE_PATH).size(width=100), # Fixed-size sibling takes 100px
#     Text("This text fills the rest").size(width='fill-available').background_color("#27ae60").text_wrap("nowrap"),
# ).size(
#     width=400, height=150
# ).gap(
#     20
# ).padding(
#     10
# ).background_color("#ecf0f1")

# Parent container with nowrap - children should inherit this
no_wrap_container = Column(
    Text("Child 1: " + LONG_TEXT[:50]),
    Text("Child 2: " + LONG_TEXT[50:100]),
    Text("Child 3: " + LONG_TEXT[100:150]),
).text_wrap("nowrap").size(width=250).background_color("#FFF0E6").padding(10).gap(8)

# Parent container with normal wrapping (default)
wrap_container = Column(
    Text("Child A: " + LONG_TEXT[:50]),
    Text("Child B: " + LONG_TEXT[50:100]),
    Text("Child C: " + LONG_TEXT[100:150]),
).size(width=250).background_color("#E6FFE6").padding(10).gap(8)

layout = Row(no_wrap_container, wrap_container).gap(20)

canvas = Canvas().font_family(STATIC_FONT_PATH).font_size(12)

canvas.render(layout).show()