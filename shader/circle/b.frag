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
uniform float uRotationSpeed;
uniform bool uBlinkToggle;
uniform bool uCommandMode;
uniform int uIdleDisplayMode;
uniform float uFocusR1;
uniform float uFocusR2;
uniform vec3 uFocusColor;
uniform int uGrids;

// (idxRing, idxWedge, freq)
uniform vec3 uSelectedPatches[100]; // 100 x vec3
uniform int uNumSelectedPatches;

uniform float uRingEdges[100]; // 100 x float
uniform int uNumRings;

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

    // r exceeds the maxR limit, return
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

    // Locate ring and wedge
    float idxRing = 0.0;
    float idxRingGrid;
    float lowerR = 0, higherR = uRingEdges[0];
    for(int i = 0; i < uNumRings; ++i) {
        if(uRingEdges[i] < r) {
            idxRing = i + 1;
            higherR = uRingEdges[i + 1];
            lowerR = uRingEdges[i];
        }
    }

    // Convert r into (0, 1) range
    r = (r - lowerR) / (higherR - lowerR);
    for(int i = 0; i < uGrids; ++i) {
        if(r > (float(i) / float(uGrids)))
            idxRingGrid = idxRing * uGrids + i;
    }

    float w = uWedges * (atan(y, x) * INV_PI + uTime * uRotationSpeed) * 0.5;
    float wg = uWedges * uGrids * (atan(y, x) * INV_PI + uTime * uRotationSpeed) * 0.5;
    w = mod(w, uWedges);
    wg = mod(wg, uWedges * uGrids);

    float idxWedge = w - mod(w, 1);
    float idxWedgeGrid = wg - mod(wg, 1);
    float checkboxColor = mod(idxRing + idxWedge, 2.0);
    float checkboxGridColor = mod(idxRingGrid + idxWedgeGrid, 2.0);

    if(uBlinkToggle) {
        // oColor = vec4(vec3(sin(uTime * uBlinkFreq * TWO_PI + (rn + wn) * PI)), 1.0);
        oColor = vec4(vec3(checkboxGridColor), 1.0);

        // Look at the selected patches, if it is selected, blink it.
        for(int i = 0; i < uNumSelectedPatches; ++i) {
            if(idxRing == uSelectedPatches[i].x && idxWedge == uSelectedPatches[i].y) {
                float freq = uSelectedPatches[i].z;
                oColor = vec4(vec3(sin(uTime * freq * TWO_PI + (idxRingGrid + idxWedgeGrid) * PI)), 1.0);
            }
        }

        return;

    }

    // Idle display in gradient
    if(uIdleDisplayMode == 0) {
        oColor = vec4(vec3(mod(w, 1.0)) * r, 1.0);
    }

    // Idle display in checkbox
    if(uIdleDisplayMode == 1) {
        oColor = vec4(vec3(checkboxColor), 1.0);
    }

    // Idle display in checkbox grid
    if(uIdleDisplayMode == 2) {
        oColor = vec4(vec3(checkboxGridColor), 1.0);
    }

    // Look at the selected patches, if it is selected, highlight it.
    for(int i = 0; i < uNumSelectedPatches; ++i) {
        if(idxRing == uSelectedPatches[i].x && idxWedge == uSelectedPatches[i].y)
            oColor = mix(oColor, vec4(1.0, 0.0, 0.0, 1.0), 0.5);
    }

    return;

}