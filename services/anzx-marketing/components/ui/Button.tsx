"use client";

import { ButtonHTMLAttributes, ReactNode } from 'react';
// import { motion } from 'framer-motion'; // Temporarily disabled
import { Star } from 'lucide-react';
import { cn } from '@/lib/utils/cn';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  icon?: ReactNode;
  showStarIcon?: boolean;
  children: ReactNode;
}

export function Button({
  variant = 'primary',
  size = 'md',
  icon,
  showStarIcon = false,
  className,
  children,
  ...props
}: ButtonProps) {
  const baseStyles =
    'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

  const variants = {
    primary:
      'bg-gradient-to-r from-teal-500 to-teal-400 text-white font-bold shadow-2xl hover:shadow-[0_20px_40px_rgba(20,184,166,0.5)] focus:ring-teal-400',
    secondary:
      'bg-white/20 backdrop-blur-sm border-2 border-white/30 text-white font-bold hover:bg-white/30 hover:shadow-xl focus:ring-white',
    outline:
      'border-2 border-teal-400 text-white hover:bg-teal-400 hover:text-white focus:ring-teal-400',
  };

  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };

  return (
    <button
      className={cn(baseStyles, variants[variant], sizes[size], className)}
      {...props}
    >
      {showStarIcon && <Star className="w-4 h-4 mr-2 fill-current" />}
      {icon && <span className="mr-2">{icon}</span>}
      {children}
    </button>
  );
}

export function PrimaryButton(props: Omit<ButtonProps, 'variant'>) {
  return <Button variant="primary" showStarIcon {...props} />;
}

export function SecondaryButton(props: Omit<ButtonProps, 'variant'>) {
  return <Button variant="secondary" {...props} />;
}

export function OutlineButton(props: Omit<ButtonProps, 'variant'>) {
  return <Button variant="outline" {...props} />;
}
