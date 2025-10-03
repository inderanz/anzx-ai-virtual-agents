"use client";

import { ButtonHTMLAttributes, ReactNode } from 'react';
import { motion } from 'framer-motion';
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
      'bg-gradient-to-r from-anzx-blue to-anzx-blue-dark text-white hover:shadow-lg focus:ring-anzx-blue',
    secondary:
      'bg-gradient-to-r from-anzx-orange to-anzx-orange-dark text-white hover:shadow-lg focus:ring-anzx-orange',
    outline:
      'border-2 border-anzx-blue text-anzx-blue hover:bg-anzx-blue hover:text-white focus:ring-anzx-blue',
  };

  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };

  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={cn(baseStyles, variants[variant], sizes[size], className)}
      {...props}
    >
      {showStarIcon && <Star className="w-4 h-4 mr-2 fill-current" />}
      {icon && <span className="mr-2">{icon}</span>}
      {children}
    </motion.button>
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
