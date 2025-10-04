'use client';

import { useEffect, useState } from 'react';

export default function MouseTrailEffect() {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (!isMounted) return;

    let mouseX = 0;
    let mouseY = 0;

    const createMouseTrail = (e: MouseEvent) => {
      mouseX = e.clientX;
      mouseY = e.clientY;

      // Only create trail sometimes for performance
      if (Math.random() > 0.7) {
        const trail = document.createElement('div');
        trail.style.position = 'fixed';
        trail.style.left = mouseX - 3 + 'px';
        trail.style.top = mouseY - 3 + 'px';
        trail.style.width = '6px';
        trail.style.height = '6px';
        trail.style.background = 'rgba(102, 126, 234, 0.6)';
        trail.style.borderRadius = '50%';
        trail.style.pointerEvents = 'none';
        trail.style.zIndex = '9998';
        trail.style.animation = 'trailFade 0.8s ease-out forwards';
        
        document.body.appendChild(trail);
        
        setTimeout(() => {
          if (trail.parentNode) {
            trail.remove();
          }
        }, 800);
      }
    };

    const updateParallax = (e: MouseEvent) => {
      const centerX = window.innerWidth / 2;
      const centerY = window.innerHeight / 2;
      const deltaX = (e.clientX - centerX) / centerX;
      const deltaY = (e.clientY - centerY) / centerY;

      // Update floating circles
      const circles = document.querySelectorAll('.floating-circle');
      circles.forEach((circle, index) => {
        const element = circle as HTMLElement;
        const multiplier = (index + 1) * 0.5;
        element.style.transform = `translate(${deltaX * 10 * multiplier}px, ${deltaY * 10 * multiplier}px)`;
      });

      // Update hero background
      const hero = document.querySelector('.hero');
      if (hero) {
        const heroElement = hero as HTMLElement;
        const rect = heroElement.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;
        
        // Update CSS custom properties for dynamic lighting
        document.documentElement.style.setProperty('--mouse-x', x + '%');
        document.documentElement.style.setProperty('--mouse-y', y + '%');
      }
    };

    const handleMouseMove = (e: MouseEvent) => {
      createMouseTrail(e);
      updateParallax(e);
    };

    document.addEventListener('mousemove', handleMouseMove);

    // Add CSS for trail animation
    const style = document.createElement('style');
    style.textContent = `
      @keyframes trailFade {
        0% {
          transform: scale(1);
          opacity: 1;
        }
        100% {
          transform: scale(0);
          opacity: 0;
        }
      }
    `;
    document.head.appendChild(style);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      if (style.parentNode) {
        style.remove();
      }
    };
  }, [isMounted]);

  if (!isMounted) return null;

  return null; // This component only adds event listeners
}