import matplotlib.pyplot as plt
import matplotlib.patches as patches
from functools import reduce

class Image(object):
    """
    An Image. Please see functions such as rectangle, square, circle, above,
    beside, etc. to learn how to construct images. Images displayed as the
    value of a Jupyter cell will draw themselves.
    """
    
    fill = "none"
    outline = "none"

    def __init__(self, width, height, mode, color):
        self.width = width
        self.height = height
        if mode == "solid":
            self.fill = color
        elif mode == "outline":
            self.outline = color
        else:
            raise ValueError("expected a mode, given %s" % mode)

    def __repr__(self):
        draw(self)
        return object.__repr__(self)

    def draw(self, canvas, x, y):
        pass

    def check(self, canvas, x, y, z):
        pass

    def __eq__(self, other):
        if (not isinstance(other, Image)): return False

        c1 = []
        c2 = []
        self.check(c1, 0, 0, 0)
        other.check(c2, 0, 0, 0)

        c1.sort()
        c2.sort()

        return c1 == c2

def rectangle(width: float, height: float, mode: str, color: str) -> Image:
    """
    returns a rectangle Image with the given height and width in the given
    fill mode (which must be "outline" or "solid") and color. The color can be
    a color word like "red", "green", or "blue" or an HTML hexadecimal color
    specifier. For more on hexadecimal color specifiers, please see
    https://www.w3schools.com/colors/colors_hexadecimal.asp
    
    (width and height must be >= 0.)
    """
    assert width >= 0, "Width must be zero or more, given width = %f" % width
    assert height >= 0, "Height must be zero or more, given width = %f" % height
    return Rectangle(width, height, mode, color)

class Rectangle(Image):
    def draw(self, canvas, x, y):
        if (self.width * self.height == 0): return

        canvas.add_patch(patches.Rectangle((x,y),
            self.width, self.height,
            fc = self.fill,
            ec = self.outline))

    def check(self, canvas, x, y, z):
        if (self.width * self.height == 0): return
        canvas.append("r %d %d %d %d %d %s %s" % (x, y,
            self.width + x, self.height + y,
            z,
            self.fill,
            self.outline))

def square(side_length: float, mode: str, color: str) -> Image:
    """
    returns a square Image with the given side length (height and width) in the given
    fill mode (which must be "outline" or "solid") and color. The color can be
    a color word like "red", "green", or "blue" or an HTML hexadecimal color
    specifier. For more on hexadecimal color specifiers, please see
    https://www.w3schools.com/colors/colors_hexadecimal.asp
    
    (side_length must be >= 0.)
    """
    assert side_length >= 0, "side_length must be zero or more, given width = %f" % side_length
    return Square(side_length, mode, color)

class Square(Rectangle):
    def __init__(self, side, mode, color):
        super(Square, self).__init__(side, side, mode, color)

def ellipse(width: float, height: float, mode: str, color: str) -> Image:
    """
    returns an elliptical Image with the given height and width in the given
    fill mode (which must be "outline" or "solid") and color. The color can be
    a color word like "red", "green", or "blue" or an HTML hexadecimal color
    specifier. For more on hexadecimal color specifiers, please see
    https://www.w3schools.com/colors/colors_hexadecimal.asp
    
    (width and height must be >= 0.)
    """
    assert width >= 0, "Width must be zero or more, given width = %f" % width
    assert height >= 0, "Height must be zero or more, given width = %f" % height
    return Ellipse(width, height, mode, color)

class Ellipse(Image):
    def draw(self, canvas, x, y):
        if (self.width * self.height == 0): return

        canvas.add_patch(patches.Ellipse((x + self.width / 2, y + self.height / 2),
            self.width, self.height,
            fc = self.fill,
            ec = self.outline))

    def check(self, canvas, x, y, z):
        if (self.width * self.height == 0): return
        canvas.append("e %d %d %d %d %d %s %s" % (x, y,
            self.width + x, self.height + y,
            z,
            self.fill,
            self.outline))

def circle(radius: float, mode: str, color: str) -> Image:
    """
    returns a circular Image with the given radius in the given
    fill mode (which must be "outline" or "solid") and color. The color can be
    a color word like "red", "green", or "blue" or an HTML hexadecimal color
    specifier. For more on hexadecimal color specifiers, please see
    https://www.w3schools.com/colors/colors_hexadecimal.asp
    
    (radius must be >= 0.)
    """
    assert radius >= 0, "radius must be zero or more, given width = %f" % radius
    return Circle(radius, mode, color)

class Circle(Ellipse):
    def __init__(self, radius, mode, color):
        super(Ellipse, self).__init__(radius * 2, radius * 2, mode, color)

def triangle(width: float, height: float, mode: str, color: str) -> Image:
    """
    returns a triangular Image with the given height and width in the given
    fill mode (which must be "outline" or "solid") and color. The color can be
    a color word like "red", "green", or "blue" or an HTML hexadecimal color
    specifier. For more on hexadecimal color specifiers, please see
    https://www.w3schools.com/colors/colors_hexadecimal.asp
    
    The triangle's base is width wide, with its apex in the center of the 
    image height above the base.
    
    (width and height must be >= 0.)
    """
    assert width >= 0, "Width must be zero or more, given width = %f" % width
    assert height >= 0, "Height must be zero or more, given width = %f" % height
    return Triangle(width, height, mode, color)

class Triangle(Image):
    def draw(self, canvas, x, y):
        if (self.width * self.height == 0): return

        canvas.add_patch(patches.Polygon(((x + self.width / 2, y + self.height),
                (x, y),
                (x + self.width, y)),
                fc = self.fill,
                ec = self.outline))

    def check(self, canvas, x, y, z):
        if (self.width * self.height == 0): return
        canvas.append("t %d %d %d %d %d %s %s" % (x, y,
            self.width + x, self.height + y,
            z,
            self.fill,
            self.outline))

class glue(Image):
    shapes = []
    def __init__(self, *shapes):
        self.shapes = shapes
        self.width = self.calculate_width()
        self.height = self.calculate_height()

    def calculate_width():
        pass
    def calculate_height():
        pass

def beside(*shapes: Image) -> Image:
    """
    returns an Image created by placing the Images given as arguments side-by-side.
    
    Note that you may pass as many arguments as you would like to beside.
    For example, beside(square(10, "solid", "blue"), circle(15, "outline", "red")) or
    beside(square(10, "solid", "blue"), circle(15, "outline", "red"), triangle(30, 30, "solid", "green")).
    """
    return Beside(*shapes)

class Beside(glue):
    def calculate_width(self):
        def add(a, b): return a + b.width
        return reduce(add, self.shapes, 0)

    def calculate_height(self):
        def m(a, b): return max(a, b.height)
        return reduce(m, self.shapes, 0)

    def draw(self, canvas, x, y):
        xc = x
        for s in self.shapes:
            s.draw(canvas, xc, y + (self.height - s.height) / 2)
            xc += s.width

    def check(self, canvas, x, y ,z):
        xc = x
        for s in self.shapes:
            s.check(canvas, xc, y, z)
            xc += s.width

def above(*shapes: Image) -> Image:
    """
    returns an Image created by placing the Images given as arguments one above the next.
    
    Note that you may pass as many arguments as you would like to above.
    For example, above(square(10, "solid", "blue"), circle(15, "outline", "red")) or
    above(square(10, "solid", "blue"), circle(15, "outline", "red"), triangle(30, 30, "solid", "green")).
    """
    return Above(*shapes)

class Above(glue):
    def calculate_width(self):
        def m(a, b): return max(a, b.width)
        return reduce(m, self.shapes, 0)

    def calculate_height(self):
        def add(a, b): return a + b.height
        return reduce(add, self.shapes, 0)

    def draw(self, canvas, x, y):
        yc = y
        for s in reversed(self.shapes):
            s.draw(canvas, x + (self.width - s.width) / 2, yc)
            yc += s.height

    def check(self, canvas, x, y ,z):
        yc = y
        for s in self.shapes:
            s.check(canvas, x, yc, z)
            yc += s.height

def overlay(*shapes: Image) -> Image:
    """
    returns an Image created by placing the Images given as arguments
    with the first image drawn centered in front of the next, which is
    in front of the next, etc.
    
    Note that you may pass as many arguments as you would like to overlay.
    For example, overlay(square(10, "solid", "blue"), circle(15, "outline", "red")) or
    overlay(square(10, "solid", "blue"), circle(15, "outline", "red"), triangle(30, 30, "solid", "green")).
    """
    return Overlay(*shapes)

class Overlay(glue):
    def calculate_width(self):
        def m(a, b): return max(a, b.width)
        return reduce(m, self.shapes, 0)

    def calculate_height(self):
        def m(a, b): return max(a, b.height)
        return reduce(m, self.shapes, 0)

    def draw(self, canvas, x, y):
        for s in reversed(self.shapes):
            s.draw(canvas, x + (self.width - s.width) / 2, y + (self.height - s.height) / 2)

    def check(self, canvas, x, y, z):
        zc = z
        for s in reversed(self.shapes):
            s.check(canvas, x, y, zc)
            zc += 1

def draw(shape: Image) -> None:
    """
    draw shape to the screen in a Jupyter notebook.
    """
    
    if (shape.width * shape.height == 0): return
    
    # Very small images (less than 1x1, where the image is scaled down to 3/4 size)
    # do not draw properly. So, we pad.
    if shape.width < 1 / 0.75:
        shape = beside(shape, square(1.5, "solid", "white"))
    if shape.height < 1 / 0.75:
        shape = above(shape, square(1.5, "solid", "white"))
    
    fig = plt.figure(figsize=(shape.width/96, shape.height/96))
    ax = plt.Axes(fig,[0,0,1,1])
    ax.axis((-2, shape.width + 2, -2, shape.height + 2))
    ax.set_axis_off()
    fig.add_axes(ax)

    shape.draw(ax, 0, 0)

# Image primitives

def image_width(shape: Image) -> float:
    """
    return the width of shape
    """
    
    return shape.width

def image_height(shape: Image) -> float:
    """
    return the height of shape
    """
    
    return shape.height

empty_image = Image(0,0,"solid","white")

# be aware that the overall cs103 library has its own __all__
__all__ = [
    'Image',
    'rectangle',
    'square',
    'ellipse',
    'circle',
    'triangle',
    'beside',
    'above',
    'overlay',
    'draw',
    'image_width',
    'image_height',
    'empty_image',
    'Beside',
    'Circle',
    'Square',
    'Rectangle',
    'Triangle',
    'Above',
    'Overlay'
]
