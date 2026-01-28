#version 330 core

// Math constants
#ifndef MATH_CONSTANTS_GLSL
#define MATH_CONSTANTS_GLSL

const float PI = 3.14159265358979323846;
const float TWO_PI = 6.28318530717958647692;
const float HALF_PI = 1.57079632679489661923;
const float INV_PI = 0.31830988618379067154;
const float INV_TWO_PI = 0.15915494309189533577;

const float E = 2.71828182845904523536;
const float GOLDEN_RATIO = 1.61803398874989484820;

#endif

in vec4 color;
in vec3 pos;
out vec4 oColor;

uniform float uRatio;
uniform float uTime;
uniform float uMaxR;
uniform int uWedges;
uniform int uRings;
uniform float uRotationSpeed;
uniform float uBlinkFreq;
uniform bool uBlinkToggle;

float dist(float x, float y) {
    return sqrt(x * x + y * y);
}

void main() {
    float y = pos.y;
    float x = pos.x * uRatio;
    float r = dist(x, y);

    if(r > uMaxR) {
        oColor = vec4(0.0);
    } else {
        r /= uMaxR;
        r *= uRings;

        float w = uWedges * (atan(y, x) * INV_PI + uTime * uRotationSpeed) * 0.5;

        if(uBlinkToggle) {
            float rn = r - mod(r, 1);
            float wn = w - mod(w, 1);
            oColor = vec4(vec3(sin(uTime * uBlinkFreq * TWO_PI + (rn + wn) * PI)), 1.0);
        } else {
            oColor = vec4(vec3(mod(w, 1.0)) * mod(r, 1.0), 1.0);
        }

        // oColor = vec4(vec3(a2), 1.0);
    }

}