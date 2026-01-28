#version 330 core

layout(location = 0) in vec2 aPos;
layout(location = 1) in vec2 nPos;
out vec2 scaledXY;
uniform mat4 projection;

void main() {
    gl_Position = projection * vec4(aPos, 0.0, 1.0);
    scaledXY = nPos;
}