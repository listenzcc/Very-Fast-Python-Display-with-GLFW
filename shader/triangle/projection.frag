#version 330 core

in vec2 scaledXY;
out vec4 FragColor;
uniform vec4 uColor;

void main()
{
    FragColor = vec4(uColor);
    // FragColor = vec4(scaledXY, 0.0, 1.0);
    FragColor.a = exp(- 1.0 * length(scaledXY-0.5));
}