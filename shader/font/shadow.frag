#version 330 core

in vec2 TexCoord;
out vec4 FragColor;

uniform sampler2D textTexture;
uniform vec3 textColor;

void main()
{
    // 阴影颜色
    vec3 shadowColor = vec3(1.0) - textColor; //vec3(1.0, 1.0, 1.0);
    // 阴影偏移量
    vec2 shadowOffset = vec2(0.05, 0.05);
    // 获取阴影的alpha值
    float shadowAlpha = texture(textTexture, TexCoord - shadowOffset).r;
    
    // 获取主文本的alpha值
    float alpha = texture(textTexture, TexCoord).r;
    
    // 混合阴影和文本
    vec4 shadow = vec4(shadowColor, shadowAlpha * 1.0); // 阴影透明度
    vec4 text = vec4(textColor, alpha);
    
    // 先绘制阴影，再在其上绘制文本
    FragColor = mix(shadow, text, text.a);
}