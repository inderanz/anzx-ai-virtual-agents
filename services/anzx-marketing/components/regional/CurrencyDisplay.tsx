'use client';

import { cn } from '@/lib/utils';

interface CurrencyDisplayProps {
  amount: number;
  currency: string;
  className?: string;
}

export function CurrencyDisplay({ amount, currency, className }: CurrencyDisplayProps) {
  const formatCurrency = (amount: number, currency: string) => {
    const formatters: Record<string, Intl.NumberFormat> = {
      AUD: new Intl.NumberFormat('en-AU', { style: 'currency', currency: 'AUD' }),
      NZD: new Intl.NumberFormat('en-NZ', { style: 'currency', currency: 'NZD' }),
      INR: new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }),
      SGD: new Intl.NumberFormat('en-SG', { style: 'currency', currency: 'SGD' }),
      USD: new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }),
    };

    const formatter = formatters[currency] || formatters.USD;
    return formatter.format(amount);
  };

  return (
    <span className={cn('font-semibold', className)}>
      {formatCurrency(amount, currency)}
    </span>
  );
}

// Legacy component for backward compatibility
interface LegacyCurrencyDisplayProps {
  currency: string;
  countryCode: string;
  plans: {
    starter: number;
    professional: number;
    enterprise: string;
  };
}

export default function LegacyCurrencyDisplay({ currency, countryCode, plans }: LegacyCurrencyDisplayProps) {
  // This is kept for backward compatibility but not used in new components
  return null;
}