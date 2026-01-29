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
uniform bool uCommandMode;
uniform int uDumpMode;
uniform float uFocusR1;
uniform float uFocusR2;
uniform vec3 uFocusColor;
uniform vec3 uVector[100]; // 100 x vec3

float dist(float x, float y) {
    return sqrt(x * x + y * y);
}

void main() {
    float y = pos.y;
    float x = pos.x * uRatio;
    float r = dist(x, y);

    // Default color
    oColor = vec4(vec3(0.0), 0.5);

    if(uCommandMode) {
        oColor = vec4(vec3(0.2), 0.8);
    }

    // r exceeds the maxR limit show nothing and return
    if(r > uMaxR) {
        return;
    }

    // Focus point
    if(r < uFocusR1) {
        oColor = vec4(uFocusColor, 1.0);
        return;
    }

    if(r < uFocusR2 && abs(x) > uFocusR1 && abs(y) > uFocusR1) {
        oColor = vec4(uFocusColor, 1.0);
        return;
    }

    r /= uMaxR;
    r *= uRings;

    float w = uWedges * (atan(y, x) * INV_PI + uTime * uRotationSpeed) * 0.5;

    w = mod(w, uWedges);

    float rn = r - mod(r, 1);
    float wn = w - mod(w, 1);
    float checkboxX = mod(rn + wn, 2.0);

    if(uBlinkToggle) {
        // oColor = vec4(vec3(sin(uTime * uBlinkFreq * TWO_PI + (rn + wn) * PI)), 1.0);
        oColor = vec4(vec3(checkboxX), 1.0);

        // Look at the selected patches, if it is selected, blink it.
        for(int i = 0; i < 100; ++i) {
            if(rn == uVector[i].x && wn == uVector[i].y) {
                float freq = uVector[i].z;
                oColor = vec4(vec3(sin(uTime * freq * TWO_PI + (rn + wn) * PI)), 1.0);
            }
        }

    } else {
        if(uDumpMode == 1) {
            // Dump mode is gradient
            oColor = vec4(vec3(mod(w, 1.0)) * mod(r, 1.0), 1.0);
        }
        if(uDumpMode == 2) {
            // Dump mode is check box
            oColor = vec4(vec3(checkboxX), 1.0);
        }

        // Look at the selected patches, if it is selected, highlight it.
        for(int i = 0; i < 100; ++i) {
            if(rn == uVector[i].x && wn == uVector[i].y)
                oColor = vec4(1.0, 0.0, 0.0, 1.0);
        }
    }

    // oColor = vec4(vec3(a2), 1.0);

}