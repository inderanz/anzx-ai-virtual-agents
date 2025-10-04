'use client';

import dynamic from 'next/dynamic';
import { useState, useEffect } from 'react';

const AnimatedHeadline = dynamic(
  () => import('./AnimatedHeadline').then(mod => ({ default: mod.AnimatedHeadline })),
  { 
    ssr: false,
    loading: () => (
      <span className="inline-block">
        Customer Service
      </span>
    )
  }
);

interface ClientOnlyAnimatedHeadlineProps {
  words?: string[];
  speedMs?: number;
  className?: string;
}

export default function ClientOnlyAnimatedHeadline(props: ClientOnlyAnimatedHeadlineProps) {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return (
      <span className={`inline-block ${props.className || ''}`}>
        {props.words?.[0] || 'Customer Service'}
      </span>
    );
  }

  return <AnimatedHeadline {...props} />;
}