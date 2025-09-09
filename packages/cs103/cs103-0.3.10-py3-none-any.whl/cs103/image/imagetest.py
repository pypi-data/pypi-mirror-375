from image import *

draw(square(1, "solid", "black"))  # should produce no errors, despite being small
draw(Beside(Square(20, "solid", "red"), Square(20, "solid", "green")))
draw(Overlay(Above(Square(20, "solid", "blue"),
                   Square(20, "solid", "green")),
             Rectangle(400, 400, "solid", "white")))

print(image_width(Beside(Square(20, "solid", "red"), Square(20, "solid", "green"))))

a = Square(100, "solid", "red")
b = Square(100, "solid", "blue")

aa = Beside(Above(a,b),Above(b,a))
bb = Above(Beside(a,b),Beside(b,a))

draw(aa)
draw(bb)

print( aa == bb)

#Circle used to be a square and triangle used to be a rectangle :( 


c = Circle(100, "solid", "red")
c2= circle(100, "solid", "red")

draw(Triangle(100,150,"solid","blue"))
draw(triangle(100,150,"solid","blue"))

draw(c)
draw(c2)

