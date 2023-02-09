import glfw
from OpenGL.GL import *
import numpy as np

def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glBegin(type)
    for i in range(12):
        glVertex2f(np.cos(np.radians(30*i)),np.sin(np.radians(30*i)))
    glEnd()


def key_callback(window,key,scancode,action,mods):
    global type
    if key==glfw.KEY_1:
        type=GL_POINTS
    elif key==glfw.KEY_2:
        type=GL_LINES
    elif key==glfw.KEY_3:
        type=GL_LINE_STRIP
    elif key==glfw.KEY_4:
        type=GL_LINE_LOOP
    elif key==glfw.KEY_5:
        type=GL_TRIANGLES
    elif key==glfw.KEY_6:
        type=GL_TRIANGLE_STRIP
    elif key==glfw.KEY_7:
        type=GL_TRIANGLE_FAN
    elif key==glfw.KEY_8:
        type=GL_QUADS
    elif key==glfw.KEY_9:
        type=GL_QUAD_STRIP
    elif key==glfw.KEY_0:
        type=GL_POLYGON
    

def main():
    global type
    
    if not glfw.init():
        return
    window=glfw.create_window(480,480,"2020059152-2-1", None, None)
    if not window:
        glfw.terminate()
        return
    
    glfw.set_key_callback(window, key_callback)
    
    glfw.make_context_current(window)
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)
    glfw.terminate
   

if __name__ == "__main__":
    type=GL_LINE_LOOP
    main()    
