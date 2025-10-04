'use client';

import dynamic from 'next/dynamic';
import { useState, useEffect } from 'react';

const WebGLFluidBackground = dynamic(
  () => import('./WebGLFluidBackground'),
  { 
    ssr: false,
    loading: () => (
      <div 
        className="absolute inset-0 w-full h-full pointer-events-none"
        style={{ 
          background: 'linear-gradient(135deg, rgba(30, 64, 175, 0.1) 0%, rgba(59, 130, 246, 0.1) 50%, rgba(96, 165, 250, 0.1) 100%)',
          zIndex: -1
        }}
      />
    )
  }
);

interface ClientOnlyWebGLProps {
  className?: string;
  intensity?: number;
  colorScheme?: 'blue' | 'purple' | 'gradient';
}

export default function ClientOnlyWebGL(props: ClientOnlyWebGLProps) {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return (
      <div 
        className={`absolute inset-0 w-full h-full pointer-events-none ${props.className || ''}`}
        style={{ 
          background: 'linear-gradient(135deg, rgba(30, 64, 175, 0.1) 0%, rgba(59, 130, 246, 0.1) 50%, rgba(96, 165, 250, 0.1) 100%)',
          zIndex: -1
        }}
      />
    );
  }

  return <WebGLFluidBackground {...props} />;
}