'use client';

import { useEffect, useRef, useCallback } from 'react';

interface WebGLFluidBackgroundProps {
  className?: string;
  intensity?: number;
  colorScheme?: 'blue' | 'purple' | 'gradient';
}

export default function WebGLFluidBackground({ 
  className = '', 
  intensity = 0.5,
  colorScheme = 'blue'
}: WebGLFluidBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const glRef = useRef<WebGLRenderingContext | null>(null);
  const programRef = useRef<WebGLProgram | null>(null);
  const animationRef = useRef<number>();
  const timeRef = useRef(0);
  const mouseRef = useRef({ x: 0.5, y: 0.5, prevX: 0.5, prevY: 0.5 });
  const velocityRef = useRef({ x: 0, y: 0 });

  const vertexShaderSource = `
    attribute vec2 a_position;
    varying vec2 v_uv;
    
    void main() {
      gl_Position = vec4(a_position, 0.0, 1.0);
      v_uv = a_position * 0.5 + 0.5;
    }
  `;

  const fragmentShaderSource = `
    precision highp float;
    
    uniform float u_time;
    uniform vec2 u_resolution;
    uniform vec2 u_mouse;
    uniform vec2 u_velocity;
    uniform float u_intensity;
    uniform int u_colorScheme;
    
    varying vec2 v_uv;
    
    // Hash function for noise
    float hash(vec2 p) {
      return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
    }
    
    // Smooth noise
    float noise(vec2 p) {
      vec2 i = floor(p);
      vec2 f = fract(p);
      f = f * f * (3.0 - 2.0 * f);
      
      float a = hash(i);
      float b = hash(i + vec2(1.0, 0.0));
      float c = hash(i + vec2(0.0, 1.0));
      float d = hash(i + vec2(1.0, 1.0));
      
      return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
    }
    
    // Fractal Brownian Motion
    float fbm(vec2 p) {
      float value = 0.0;
      float amplitude = 0.5;
      float frequency = 1.0;
      
      for(int i = 0; i < 5; i++) {
        value += amplitude * noise(p * frequency);
        amplitude *= 0.5;
        frequency *= 2.0;
      }
      
      return value;
    }
    
    // Fluid simulation approximation
    vec2 curl(vec2 p) {
      float eps = 0.01;
      float n1 = fbm(p + vec2(eps, 0.0));
      float n2 = fbm(p - vec2(eps, 0.0));
      float n3 = fbm(p + vec2(0.0, eps));
      float n4 = fbm(p - vec2(0.0, eps));
      
      return vec2(n3 - n4, n2 - n1) / (2.0 * eps);
    }
    
    void main() {
      vec2 uv = v_uv;
      vec2 p = uv * 3.0;
      
      // Time-based animation
      float time = u_time * 0.3;
      
      // Mouse influence
      vec2 mousePos = u_mouse;
      float mouseDist = length(uv - mousePos);
      vec2 mouseForce = (uv - mousePos) * exp(-mouseDist * 3.0) * u_intensity;
      
      // Velocity influence
      vec2 vel = u_velocity * 0.1;
      
      // Create fluid motion
      p += curl(p + time * 0.1) * 0.3;
      p += mouseForce * 2.0;
      p += vel;
      
      // Generate fluid patterns
      float pattern1 = fbm(p + time * 0.05);
      float pattern2 = fbm(p * 1.5 - time * 0.08);
      float pattern3 = fbm(p * 2.0 + curl(p) * 0.5);
      
      // Combine patterns
      float combined = pattern1 * 0.5 + pattern2 * 0.3 + pattern3 * 0.2;
      combined = smoothstep(0.1, 0.9, combined);
      
      // Color schemes
      vec3 color;
      if (u_colorScheme == 0) { // Blue
        vec3 color1 = vec3(0.1, 0.2, 0.8);
        vec3 color2 = vec3(0.2, 0.5, 1.0);
        vec3 color3 = vec3(0.4, 0.7, 1.0);
        color = mix(mix(color1, color2, combined), color3, smoothstep(0.5, 1.0, combined));
      } else if (u_colorScheme == 1) { // Purple
        vec3 color1 = vec3(0.3, 0.1, 0.8);
        vec3 color2 = vec3(0.6, 0.2, 1.0);
        vec3 color3 = vec3(0.8, 0.4, 1.0);
        color = mix(mix(color1, color2, combined), color3, smoothstep(0.5, 1.0, combined));
      } else { // Gradient
        vec3 color1 = vec3(0.1, 0.2, 0.8);
        vec3 color2 = vec3(0.6, 0.2, 1.0);
        vec3 color3 = vec3(0.2, 0.8, 0.6);
        color = mix(mix(color1, color2, combined), color3, smoothstep(0.5, 1.0, combined));
      }
      
      // Add some glow and transparency
      float alpha = combined * 0.4 + 0.1;
      alpha *= (1.0 - mouseDist * 0.5); // Fade away from mouse
      
      // Add subtle animation
      alpha += sin(time + uv.x * 10.0) * 0.05;
      alpha += cos(time * 0.7 + uv.y * 8.0) * 0.03;
      
      gl_FragColor = vec4(color, alpha);
    }
  `;

  const createShader = useCallback((gl: WebGLRenderingContext, type: number, source: string): WebGLShader | null => {
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
  }, []);

  const createProgram = useCallback((gl: WebGLRenderingContext, vertexShader: WebGLShader, fragmentShader: WebGLShader): WebGLProgram | null => {
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
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const gl = canvas.getContext('webgl', { 
      alpha: true, 
      premultipliedAlpha: false,
      antialias: true
    });
    
    if (!gl) {
      console.warn('WebGL not supported');
      return;
    }

    glRef.current = gl;

    // Create shaders and program
    const vertexShader = createShader(gl, gl.VERTEX_SHADER, vertexShaderSource);
    const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, fragmentShaderSource);
    
    if (!vertexShader || !fragmentShader) return;
    
    const program = createProgram(gl, vertexShader, fragmentShader);
    if (!program) return;
    
    programRef.current = program;

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

    // Get locations
    const positionLocation = gl.getAttribLocation(program, 'a_position');
    const timeLocation = gl.getUniformLocation(program, 'u_time');
    const resolutionLocation = gl.getUniformLocation(program, 'u_resolution');
    const mouseLocation = gl.getUniformLocation(program, 'u_mouse');
    const velocityLocation = gl.getUniformLocation(program, 'u_velocity');
    const intensityLocation = gl.getUniformLocation(program, 'u_intensity');
    const colorSchemeLocation = gl.getUniformLocation(program, 'u_colorScheme');

    let lastTime = 0;

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

    function render(currentTime: number) {
      if (!gl || !canvas) return;
      const deltaTime = currentTime - lastTime;
      lastTime = currentTime;
      
      timeRef.current = currentTime * 0.001;
      
      resize();
      
      gl.clearColor(0, 0, 0, 0);
      gl.clear(gl.COLOR_BUFFER_BIT);
      
      gl.useProgram(program);
      
      // Set up attributes
      gl.enableVertexAttribArray(positionLocation);
      gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
      gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);
      
      // Set uniforms
      gl.uniform1f(timeLocation, timeRef.current);
      gl.uniform2f(resolutionLocation, canvas.width, canvas.height);
      gl.uniform2f(mouseLocation, mouseRef.current.x, mouseRef.current.y);
      gl.uniform2f(velocityLocation, velocityRef.current.x, velocityRef.current.y);
      gl.uniform1f(intensityLocation, intensity);
      
      const colorSchemeValue = colorScheme === 'blue' ? 0 : colorScheme === 'purple' ? 1 : 2;
      gl.uniform1i(colorSchemeLocation, colorSchemeValue);
      
      // Enable blending
      gl.enable(gl.BLEND);
      gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
      
      // Draw
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      
      // Update velocity with decay
      velocityRef.current.x *= 0.95;
      velocityRef.current.y *= 0.95;
      
      animationRef.current = requestAnimationFrame(render);
    }

    function handleMouseMove(event: MouseEvent) {
      if (!canvas) return;
      const rect = canvas.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width;
      const y = 1.0 - (event.clientY - rect.top) / rect.height;
      
      // Calculate velocity
      velocityRef.current.x = x - mouseRef.current.x;
      velocityRef.current.y = y - mouseRef.current.y;
      
      mouseRef.current.prevX = mouseRef.current.x;
      mouseRef.current.prevY = mouseRef.current.y;
      mouseRef.current.x = x;
      mouseRef.current.y = y;
    }

    function handleMouseLeave() {
      velocityRef.current.x = 0;
      velocityRef.current.y = 0;
    }

    // Event listeners
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseleave', handleMouseLeave);
    
    // Start animation
    animationRef.current = requestAnimationFrame(render);

    // Cleanup
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      canvas.removeEventListener('mousemove', handleMouseMove);
      canvas.removeEventListener('mouseleave', handleMouseLeave);
      
      if (gl && program) {
        gl.deleteProgram(program);
      }
    };
  }, [intensity, colorScheme, createShader, createProgram]);

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