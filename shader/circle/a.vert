#version 330 core 

layout(location = 0) in vec3 iPos;
layout(location = 1) in vec4 iColor;

out vec4 color;
out vec3 pos;

uniform float uRatio;

void main() {
    gl_Position = vec4(iPos, 1.0);
    color = iColor;
    pos = iPos;
}