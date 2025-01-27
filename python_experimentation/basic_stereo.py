import math
import glm

import moderngl_window as mglw
from moderngl_window.scene.camera import Camera


class BasicStereoWindow(mglw.WindowConfig):
    gl_version = (3, 3)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.wnd.exit_key = self.wnd.keys.Q

        self.vtx_shader_src = """
            #version 330 core

            uniform mat4 camera;

            vec3 vertices[3] = vec3[](
                vec3(0.0, 0.4, 0.0),
                vec3(-0.4, -0.3, 0.0),
                vec3(0.4, -0.3, 0.0)
            );

            void main() {
                gl_Position = camera * vec4(vertices[gl_VertexID], 1.0);
            }
            """
        
        self.frag_shader_src = """
            #version 330 core

            layout (location = 0) out vec4 out_color;

            void main() {
                out_color = vec4(1.0, .0, 1.0, 1.0);
            }

            """
        
        self.program = self.ctx.program(vertex_shader=self.vtx_shader_src, fragment_shader=self.frag_shader_src)

        self.vao = self.ctx.vertex_array(self.program, [])
        self.vao.vertices = 3
        
        
    def render(self, time, frametime):
        from pyrr import Vector3
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)
        self.ctx.enable(self.ctx.DEPTH_TEST)

        eyesep = 0.15
        z = math.sin(time*2*math.pi)*8 + 10 # .9 to 1.1 

        proj = glm.perspective(math.radians(90), 1.0, 0.1, 1000.0)

        lookl = glm.lookAt((-eyesep,0, z), (0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
        lookr = glm.lookAt((eyesep,0, z), (0.0, 0.0, 0.0), (0.0, 0.0, -1.0))

        self.ctx.viewport = (0, 0, self.window_size[0]//2, self.window_size[1])
        self.program['camera'].write(proj*lookl)
        self.vao.render()

        self.ctx.viewport = (self.window_size[0]//2, 0, self.window_size[0]//2, self.window_size[1])
        self.program['camera'].write(proj*lookr)
        self.vao.render()

    def resize(self, width: int, height: int):
        self.window_size = (width, height)

    # def key_event(self, key, action, modifiers):
    #     if key == self.wnd.keys.Q:
    #         self.wnd.close()

BasicStereoWindow.run()