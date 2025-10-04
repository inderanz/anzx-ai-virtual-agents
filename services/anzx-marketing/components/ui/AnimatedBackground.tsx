'use client';

import { useEffect, useRef } from 'react';

interface AnimatedBackgroundProps {
  className?: string;
  variant?: 'fluid' | 'particles' | 'waves';
  intensity?: number;
}

export default function AnimatedBackground({ 
  className = '', 
  variant = 'fluid',
  intensity = 0.5
}: AnimatedBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const mouseRef = useRef({ x: 0, y: 0 });
  const particlesRef = useRef<Array<{
    x: number;
    y: number;
    vx: number;
    vy: number;
    size: number;
    opacity: number;
    color: string;
  }>>([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let width = 0;
    let height = 0;
    let time = 0;

    // Colors for ANZX branding
    const colors = [
      'rgba(30, 64, 175, 0.1)',   // blue-700
      'rgba(59, 130, 246, 0.1)',  // blue-500
      'rgba(96, 165, 250, 0.1)',  // blue-400
      'rgba(147, 197, 253, 0.1)', // blue-300
      'rgba(219, 234, 254, 0.1)', // blue-100
    ];

    function resize() {
      if (!canvas || !ctx) return;
      const rect = canvas.getBoundingClientRect();
      width = rect.width;
      height = rect.height;
      canvas.width = width * window.devicePixelRatio;
      canvas.height = height * window.devicePixelRatio;
      if (ctx) {
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
      }
      
      // Reinitialize particles on resize
      if (variant === 'particles') {
        initParticles();
      }
    }

    function initParticles() {
      particlesRef.current = [];
      const particleCount = Math.min(50, Math.floor((width * height) / 10000));
      
      for (let i = 0; i < particleCount; i++) {
        particlesRef.current.push({
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.5,
          vy: (Math.random() - 0.5) * 0.5,
          size: Math.random() * 3 + 1,
          opacity: Math.random() * 0.5 + 0.1,
          color: colors[Math.floor(Math.random() * colors.length)]
        });
      }
    }

    function drawFluid() {
      if (!ctx) return;
      ctx.clearRect(0, 0, width, height);
      
      // Create gradient background
      const gradient = ctx.createLinearGradient(0, 0, width, height);
      gradient.addColorStop(0, 'rgba(30, 64, 175, 0.02)');
      gradient.addColorStop(0.5, 'rgba(59, 130, 246, 0.03)');
      gradient.addColorStop(1, 'rgba(96, 165, 250, 0.02)');
      
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, width, height);

      // Draw flowing shapes
      for (let i = 0; i < 5; i++) {
        ctx.save();
        
        const offsetX = Math.sin(time * 0.001 + i * 0.5) * 100;
        const offsetY = Math.cos(time * 0.0008 + i * 0.3) * 50;
        const scale = 1 + Math.sin(time * 0.0005 + i) * 0.2;
        
        ctx.translate(width * 0.2 + offsetX + i * width * 0.15, height * 0.3 + offsetY + i * height * 0.1);
        ctx.scale(scale, scale);
        ctx.rotate(time * 0.0002 + i * 0.1);
        
        // Create blob shape
        ctx.beginPath();
        const radius = 80 + i * 20;
        for (let angle = 0; angle < Math.PI * 2; angle += 0.1) {
          const r = radius + Math.sin(angle * 3 + time * 0.002) * 20;
          const x = Math.cos(angle) * r;
          const y = Math.sin(angle) * r;
          
          if (angle === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        }
        ctx.closePath();
        
        const blobGradient = ctx.createRadialGradient(0, 0, 0, 0, 0, radius);
        blobGradient.addColorStop(0, colors[i % colors.length]);
        blobGradient.addColorStop(1, 'rgba(30, 64, 175, 0)');
        
        ctx.fillStyle = blobGradient;
        ctx.fill();
        
        ctx.restore();
      }

      // Mouse interaction
      if (mouseRef.current.x > 0 && mouseRef.current.y > 0) {
        const mouseGradient = ctx.createRadialGradient(
          mouseRef.current.x, mouseRef.current.y, 0,
          mouseRef.current.x, mouseRef.current.y, 150
        );
        mouseGradient.addColorStop(0, 'rgba(59, 130, 246, 0.1)');
        mouseGradient.addColorStop(1, 'rgba(59, 130, 246, 0)');
        
        ctx.fillStyle = mouseGradient;
        ctx.fillRect(0, 0, width, height);
      }
    }

    function drawParticles() {
      if (!ctx) return;
      ctx.clearRect(0, 0, width, height);
      
      particlesRef.current.forEach((particle, index) => {
        // Update particle position
        particle.x += particle.vx;
        particle.y += particle.vy;
        
        // Wrap around edges
        if (particle.x < 0) particle.x = width;
        if (particle.x > width) particle.x = 0;
        if (particle.y < 0) particle.y = height;
        if (particle.y > height) particle.y = 0;
        
        // Mouse interaction
        const dx = mouseRef.current.x - particle.x;
        const dy = mouseRef.current.y - particle.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance < 100) {
          const force = (100 - distance) / 100;
          particle.vx += (dx / distance) * force * 0.01;
          particle.vy += (dy / distance) * force * 0.01;
        }
        
        // Apply friction
        particle.vx *= 0.99;
        particle.vy *= 0.99;
        
        // Draw particle
        ctx.save();
        ctx.globalAlpha = particle.opacity;
        ctx.fillStyle = particle.color;
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
        
        // Draw connections
        particlesRef.current.slice(index + 1).forEach(otherParticle => {
          const dx = particle.x - otherParticle.x;
          const dy = particle.y - otherParticle.y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          
          if (distance < 100) {
            ctx.save();
            ctx.globalAlpha = (100 - distance) / 100 * 0.1;
            ctx.strokeStyle = 'rgba(59, 130, 246, 0.2)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(particle.x, particle.y);
            ctx.lineTo(otherParticle.x, otherParticle.y);
            ctx.stroke();
            ctx.restore();
          }
        });
      });
    }

    function drawWaves() {
      if (!ctx) return;
      ctx.clearRect(0, 0, width, height);
      
      // Draw multiple wave layers
      for (let layer = 0; layer < 3; layer++) {
        ctx.save();
        ctx.globalAlpha = 0.1 - layer * 0.02;
        
        ctx.beginPath();
        ctx.moveTo(0, height);
        
        for (let x = 0; x <= width; x += 10) {
          const y = height * 0.7 + 
                   Math.sin((x + time * 0.5) * 0.01 + layer) * 30 +
                   Math.sin((x + time * 0.3) * 0.005 + layer * 0.5) * 20;
          ctx.lineTo(x, y);
        }
        
        ctx.lineTo(width, height);
        ctx.closePath();
        
        const waveGradient = ctx.createLinearGradient(0, 0, 0, height);
        waveGradient.addColorStop(0, colors[layer % colors.length]);
        waveGradient.addColorStop(1, 'rgba(30, 64, 175, 0)');
        
        ctx.fillStyle = waveGradient;
        ctx.fill();
        
        ctx.restore();
      }
    }

    function animate() {
      time = Date.now();
      
      switch (variant) {
        case 'fluid':
          drawFluid();
          break;
        case 'particles':
          drawParticles();
          break;
        case 'waves':
          drawWaves();
          break;
      }
      
      animationRef.current = requestAnimationFrame(animate);
    }

    function handleMouseMove(event: MouseEvent) {
      if (!canvas) return;
      const rect = canvas.getBoundingClientRect();
      mouseRef.current.x = event.clientX - rect.left;
      mouseRef.current.y = event.clientY - rect.top;
    }

    function handleMouseLeave() {
      mouseRef.current.x = 0;
      mouseRef.current.y = 0;
    }

    // Initialize
    resize();
    if (variant === 'particles') {
      initParticles();
    }
    
    // Event listeners
    window.addEventListener('resize', resize);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseleave', handleMouseLeave);
    
    // Start animation
    animate();

    // Cleanup
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      window.removeEventListener('resize', resize);
      canvas.removeEventListener('mousemove', handleMouseMove);
      canvas.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, [variant, intensity]);

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