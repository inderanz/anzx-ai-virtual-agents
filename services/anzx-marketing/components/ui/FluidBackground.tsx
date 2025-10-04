'use client';

import { useEffect, useRef } from 'react';

interface FluidBackgroundProps {
  className?: string;
  intensity?: number;
  colors?: string[];
}

export default function FluidBackground({ 
  className = '', 
  intensity = 0.3,
  colors = ['#1e40af', '#3b82f6', '#60a5fa', '#93c5fd']
}: FluidBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const mouseRef = useRef({ x: 0, y: 0, prevX: 0, prevY: 0 });
  const timeRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const gl = canvas.getContext('webgl') as WebGLRenderingContext | null;
    if (!gl) {
      console.warn('WebGL not supported, falling back to canvas');
      return;
    }

    // Vertex shader source
    const vertexShaderSource = `
      attribute vec2 a_position;
      varying vec2 v_texCoord;
      
      void main() {
        gl_Position = vec4(a_position, 0.0, 1.0);
        v_texCoord = a_position * 0.5 + 0.5;
      }
    `;

    // Fragment shader source for fluid simulation
    const fragmentShaderSource = `
      precision mediump float;
      
      uniform float u_time;
      uniform vec2 u_resolution;
      uniform vec2 u_mouse;
      uniform float u_intensity;
      
      varying vec2 v_texCoord;
      
      // Noise function
      float noise(vec2 p) {
        return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
      }
      
      // Smooth noise
      float smoothNoise(vec2 p) {
        vec2 i = floor(p);
        vec2 f = fract(p);
        f = f * f * (3.0 - 2.0 * f);
        
        float a = noise(i);
        float b = noise(i + vec2(1.0, 0.0));
        float c = noise(i + vec2(0.0, 1.0));
        float d = noise(i + vec2(1.0, 1.0));
        
        return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
      }
      
      // Fractal noise
      float fractalNoise(vec2 p) {
        float value = 0.0;
        float amplitude = 0.5;
        
        for(int i = 0; i < 4; i++) {
          value += amplitude * smoothNoise(p);
          p *= 2.0;
          amplitude *= 0.5;
        }
        
        return value;
      }
      
      void main() {
        vec2 uv = v_texCoord;
        vec2 p = uv * 4.0;
        
        // Create flowing motion
        float time = u_time * 0.5;
        p.x += sin(time * 0.3 + uv.y * 3.0) * 0.3;
        p.y += cos(time * 0.2 + uv.x * 2.0) * 0.2;
        
        // Add mouse interaction
        vec2 mousePos = u_mouse / u_resolution;
        float mouseDist = length(uv - mousePos);
        float mouseEffect = exp(-mouseDist * 8.0) * u_intensity;
        
        p += mouseEffect * (uv - mousePos) * 2.0;
        
        // Generate fluid-like patterns
        float n1 = fractalNoise(p + time * 0.1);
        float n2 = fractalNoise(p * 1.5 - time * 0.15);
        float n3 = fractalNoise(p * 2.0 + time * 0.08);
        
        // Combine noise patterns
        float pattern = n1 * 0.5 + n2 * 0.3 + n3 * 0.2;
        pattern = smoothstep(0.2, 0.8, pattern);
        
        // Create color gradient
        vec3 color1 = vec3(0.118, 0.251, 0.686); // #1e40af
        vec3 color2 = vec3(0.231, 0.510, 0.961); // #3b82f6
        vec3 color3 = vec3(0.376, 0.647, 0.980); // #60a5fa
        
        vec3 finalColor = mix(color1, color2, pattern);
        finalColor = mix(finalColor, color3, smoothstep(0.6, 1.0, pattern));
        
        // Add some transparency and glow
        float alpha = pattern * 0.6 + 0.1;
        
        gl_FragColor = vec4(finalColor, alpha);
      }
    `;

    // Create shader function
    function createShader(gl: WebGLRenderingContext, type: number, source: string): WebGLShader | null {
      const shader = gl.createShader(type);
      if (!shader) return null;
      
      gl.shaderSource(shader, source);
      gl.compileShader(shader);
      
      if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        console.error('Shader compilation error:', gl.getShaderInfoLog(shader));
        gl.deleteShader(shader);
        return null;
      }
      
      return shader;
    }

    // Create program function
    function createProgram(gl: WebGLRenderingContext, vertexShader: WebGLShader, fragmentShader: WebGLShader): WebGLProgram | null {
      const program = gl.createProgram();
      if (!program) return null;
      
      gl.attachShader(program, vertexShader);
      gl.attachShader(program, fragmentShader);
      gl.linkProgram(program);
      
      if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
        console.error('Program linking error:', gl.getProgramInfoLog(program));
        gl.deleteProgram(program);
        return null;
      }
      
      return program;
    }

    // Initialize WebGL
    const vertexShader = createShader(gl, gl.VERTEX_SHADER, vertexShaderSource);
    const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, fragmentShaderSource);
    
    if (!vertexShader || !fragmentShader) return;
    
    const program = createProgram(gl, vertexShader, fragmentShader);
    if (!program) return;

    // Set up geometry (full screen quad)
    const positions = new Float32Array([
      -1, -1,
       1, -1,
      -1,  1,
       1,  1,
    ]);

    const positionBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, positions, gl.STATIC_DRAW);

    // Get attribute and uniform locations
    const positionAttributeLocation = gl.getAttribLocation(program, 'a_position');
    const timeUniformLocation = gl.getUniformLocation(program, 'u_time');
    const resolutionUniformLocation = gl.getUniformLocation(program, 'u_resolution');
    const mouseUniformLocation = gl.getUniformLocation(program, 'u_mouse');
    const intensityUniformLocation = gl.getUniformLocation(program, 'u_intensity');

    // Resize function
    function resize() {
      if (!canvas) return;
      const displayWidth = canvas.clientWidth;
      const displayHeight = canvas.clientHeight;
      
      if (canvas.width !== displayWidth || canvas.height !== displayHeight) {
        canvas.width = displayWidth;
        canvas.height = displayHeight;
        if (gl) {
          gl.viewport(0, 0, canvas.width, canvas.height);
        }
      }
    }

    // Mouse move handler
    function handleMouseMove(event: MouseEvent) {
      if (!canvas) return;
      const rect = canvas.getBoundingClientRect();
      mouseRef.current.prevX = mouseRef.current.x;
      mouseRef.current.prevY = mouseRef.current.y;
      mouseRef.current.x = event.clientX - rect.left;
      mouseRef.current.y = rect.height - (event.clientY - rect.top);
    }

    // Touch move handler
    function handleTouchMove(event: TouchEvent) {
      if (!canvas) return;
      event.preventDefault();
      const rect = canvas.getBoundingClientRect();
      const touch = event.touches[0];
      mouseRef.current.prevX = mouseRef.current.x;
      mouseRef.current.prevY = mouseRef.current.y;
      mouseRef.current.x = touch.clientX - rect.left;
      mouseRef.current.y = rect.height - (touch.clientY - rect.top);
    }

    // Render function
    function render() {
      if (!gl || !canvas) return;
      resize();
      
      timeRef.current += 0.016; // ~60fps
      
      gl.clearColor(0, 0, 0, 0);
      gl.clear(gl.COLOR_BUFFER_BIT);
      
      gl.useProgram(program);
      
      // Set up position attribute
      gl.enableVertexAttribArray(positionAttributeLocation);
      gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
      gl.vertexAttribPointer(positionAttributeLocation, 2, gl.FLOAT, false, 0, 0);
      
      // Set uniforms
      gl.uniform1f(timeUniformLocation, timeRef.current);
      gl.uniform2f(resolutionUniformLocation, canvas.width, canvas.height);
      gl.uniform2f(mouseUniformLocation, mouseRef.current.x, mouseRef.current.y);
      gl.uniform1f(intensityUniformLocation, intensity);
      
      // Enable blending for transparency
      gl.enable(gl.BLEND);
      gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
      
      // Draw
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      
      animationRef.current = requestAnimationFrame(render);
    }

    // Add event listeners
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('touchmove', handleTouchMove, { passive: false });
    
    // Start animation
    render();

    // Cleanup
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      canvas.removeEventListener('mousemove', handleMouseMove);
      canvas.removeEventListener('touchmove', handleTouchMove);
    };
  }, [intensity]);

  return (
    <canvas
      ref={canvasRef}
      className={`absolute inset-0 w-full h-full pointer-events-none ${className}`}
      style={{ 
        background: 'transparent',
        zIndex: -1
      }}
    />
  );
}