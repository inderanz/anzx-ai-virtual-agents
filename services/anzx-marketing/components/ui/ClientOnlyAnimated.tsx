'use client';

import dynamic from 'next/dynamic';
import { useState, useEffect } from 'react';

const AnimatedBackground = dynamic(
  () => import('./AnimatedBackground'),
  { 
    ssr: false,
    loading: () => (
      <div 
        className="absolute inset-0 w-full h-full pointer-events-none"
        style={{ 
          background: 'linear-gradient(135deg, rgba(30, 64, 175, 0.05) 0%, rgba(59, 130, 246, 0.05) 50%, rgba(96, 165, 250, 0.05) 100%)',
          zIndex: -1
        }}
      />
    )
  }
);

interface ClientOnlyAnimatedProps {
  className?: string;
  variant?: 'fluid' | 'particles' | 'waves';
  intensity?: number;
}

export default function ClientOnlyAnimated(props: ClientOnlyAnimatedProps) {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return (
      <div 
        className={`absolute inset-0 w-full h-full pointer-events-none ${props.className || ''}`}
        style={{ 
          background: 'linear-gradient(135deg, rgba(30, 64, 175, 0.05) 0%, rgba(59, 130, 246, 0.05) 50%, rgba(96, 165, 250, 0.05) 100%)',
          zIndex: -1
        }}
      />
    );
  }

  return <AnimatedBackground {...props} />;
}