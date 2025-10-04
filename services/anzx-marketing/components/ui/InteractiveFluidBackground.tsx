'use client';

import { useEffect, useRef, useState } from 'react';

interface InteractiveFluidBackgroundProps {
  className?: string;
}

export default function InteractiveFluidBackground({ className = '' }: InteractiveFluidBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isMounted, setIsMounted] = useState(false);
  const animationRef = useRef<number>();
  const mouseRef = useRef({ x: 0, y: 0 });

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (!isMounted) return;

    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const resizeCanvas = () => {
      const rect = container.getBoundingClientRect();
      canvas.width = rect.width;
      canvas.height = rect.height;
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Particle system
    const particles: Array<{
      x: number;
      y: number;
      vx: number;
      vy: number;
      size: number;
      opacity: number;
      color: string;
    }> = [];

    // Initialize particles
    const initParticles = () => {
      particles.length = 0;
      const particleCount = Math.min(50, Math.floor((canvas.width * canvas.height) / 15000));
      
      for (let i = 0; i < particleCount; i++) {
        particles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.5,
          vy: (Math.random() - 0.5) * 0.5,
          size: Math.random() * 3 + 1,
          opacity: Math.random() * 0.5 + 0.2,
          color: `rgba(${102 + Math.random() * 50}, ${126 + Math.random() * 50}, 234, ${Math.random() * 0.3 + 0.1})`
        });
      }
    };

    initParticles();

    // Mouse tracking
    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      mouseRef.current.x = e.clientX - rect.left;
      mouseRef.current.y = e.clientY - rect.top;
    };

    container.addEventListener('mousemove', handleMouseMove);

    // Animation loop
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Create gradient background
      const gradient = ctx.createRadialGradient(
        mouseRef.current.x, mouseRef.current.y, 0,
        mouseRef.current.x, mouseRef.current.y, 300
      );
      gradient.addColorStop(0, 'rgba(102, 126, 234, 0.1)');
      gradient.addColorStop(0.5, 'rgba(240, 147, 251, 0.05)');
      gradient.addColorStop(1, 'rgba(79, 172, 254, 0.02)');
      
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Update and draw particles
      particles.forEach((particle, index) => {
        // Update position
        particle.x += particle.vx;
        particle.y += particle.vy;

        // Bounce off edges
        if (particle.x <= 0 || particle.x >= canvas.width) particle.vx *= -1;
        if (particle.y <= 0 || particle.y >= canvas.height) particle.vy *= -1;

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
        particles.slice(index + 1).forEach(otherParticle => {
          const dx = particle.x - otherParticle.x;
          const dy = particle.y - otherParticle.y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < 80) {
            ctx.save();
            ctx.globalAlpha = (80 - distance) / 80 * 0.1;
            ctx.strokeStyle = 'rgba(102, 126, 234, 0.3)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(particle.x, particle.y);
            ctx.lineTo(otherParticle.x, otherParticle.y);
            ctx.stroke();
            ctx.restore();
          }
        });
      });

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      container.removeEventListener('mousemove', handleMouseMove);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isMounted]);

  if (!isMounted) {
    return (
      <div 
        className={`absolute inset-0 w-full h-full pointer-events-none ${className}`}
        style={{ 
          background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(240, 147, 251, 0.05) 50%, rgba(79, 172, 254, 0.02) 100%)',
          zIndex: -1
        }}
      />
    );
  }

  return (
    <div 
      ref={containerRef}
      className={`absolute inset-0 w-full h-full pointer-events-none ${className}`}
      style={{ zIndex: -1 }}
    >
      {/* CSS Animated Background */}
      <div className="absolute inset-0 hero-gradient animate-gradient-shift" />
      
      {/* Floating Circles */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="floating-circle circle-1" />
        <div className="floating-circle circle-2" />
        <div className="floating-circle circle-3" />
        <div className="floating-circle circle-4" />
        <div className="floating-circle circle-5" />
        <div className="floating-circle circle-6" />
      </div>

      {/* Interactive Canvas */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full"
        style={{ mixBlendMode: 'multiply' }}
      />

      <style jsx>{`
        .hero-gradient {
          background: linear-gradient(135deg, 
            rgba(102, 126, 234, 0.08) 0%, 
            rgba(118, 75, 162, 0.08) 25%, 
            rgba(240, 147, 251, 0.08) 50%, 
            rgba(79, 172, 254, 0.08) 75%, 
            rgba(0, 242, 254, 0.08) 100%);
        }

        .animate-gradient-shift {
          animation: gradientShift 15s ease-in-out infinite;
        }

        @keyframes gradientShift {
          0%, 100% { 
            background: linear-gradient(135deg, 
              rgba(102, 126, 234, 0.08) 0%, 
              rgba(118, 75, 162, 0.08) 25%, 
              rgba(240, 147, 251, 0.08) 50%, 
              rgba(79, 172, 254, 0.08) 75%, 
              rgba(0, 242, 254, 0.08) 100%);
          }
          50% { 
            background: linear-gradient(225deg, 
              rgba(240, 147, 251, 0.08) 0%, 
              rgba(79, 172, 254, 0.08) 25%, 
              rgba(0, 242, 254, 0.08) 50%, 
              rgba(102, 126, 234, 0.08) 75%, 
              rgba(118, 75, 162, 0.08) 100%);
          }
        }

        .floating-circle {
          position: absolute;
          border-radius: 50%;
          background: radial-gradient(circle at 30% 30%, 
            rgba(102, 126, 234, 0.3), 
            rgba(240, 147, 251, 0.2), 
            rgba(79, 172, 254, 0.1));
          filter: blur(2px);
          animation: floatAnimation 15s ease-in-out infinite;
        }

        .circle-1 {
          width: 100px;
          height: 100px;
          top: 10%;
          left: 10%;
          animation-delay: 0s;
          animation-duration: 20s;
        }

        .circle-2 {
          width: 150px;
          height: 150px;
          top: 20%;
          right: 20%;
          animation-delay: -5s;
          animation-duration: 25s;
        }

        .circle-3 {
          width: 80px;
          height: 80px;
          bottom: 30%;
          left: 30%;
          animation-delay: -10s;
          animation-duration: 18s;
        }

        .circle-4 {
          width: 120px;
          height: 120px;
          bottom: 20%;
          right: 10%;
          animation-delay: -15s;
          animation-duration: 22s;
        }

        .circle-5 {
          width: 60px;
          height: 60px;
          top: 50%;
          left: 50%;
          animation-delay: -8s;
          animation-duration: 16s;
        }

        .circle-6 {
          width: 200px;
          height: 200px;
          top: 60%;
          right: 40%;
          animation-delay: -12s;
          animation-duration: 30s;
        }

        @keyframes floatAnimation {
          0%, 100% { 
            transform: translateY(0px) translateX(0px) scale(1) rotate(0deg);
            opacity: 0.4;
          }
          25% { 
            transform: translateY(-30px) translateX(20px) scale(1.1) rotate(90deg);
            opacity: 0.7;
          }
          50% { 
            transform: translateY(-15px) translateX(-15px) scale(0.9) rotate(180deg);
            opacity: 0.5;
          }
          75% { 
            transform: translateY(-25px) translateX(25px) scale(1.05) rotate(270deg);
            opacity: 0.6;
          }
        }

        @media (prefers-reduced-motion: reduce) {
          .animate-gradient-shift,
          .floating-circle {
            animation: none;
          }
        }
      `}</style>
    </div>
  );
}