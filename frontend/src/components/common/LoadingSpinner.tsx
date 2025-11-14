/**
 * LoadingSpinner - Reusable loading indicator component
 *
 * Komponenty wizualizacji stanu ładowania z różnymi rozmiarami i kolorami.
 */

import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  text?: string;
}

const sizeMap = {
  sm: 'h-4 w-4',
  md: 'h-6 w-6',
  lg: 'h-8 w-8',
  xl: 'h-12 w-12',
};

export function LoadingSpinner({ size = 'md', className, text }: LoadingSpinnerProps) {
  return (
    <div className={cn('flex items-center justify-center gap-2', className)}>
      <Loader2 className={cn('animate-spin text-blue-600', sizeMap[size])} />
      {text && <span className="text-sm text-gray-600">{text}</span>}
    </div>
  );
}

export function LoadingOverlay({ text = 'Ładowanie...' }: { text?: string }) {
  return (
    <div className="absolute inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-50 rounded-lg">
      <div className="flex flex-col items-center gap-3">
        <Loader2 className="h-10 w-10 animate-spin text-blue-600" />
        <p className="text-sm font-medium text-gray-700">{text}</p>
      </div>
    </div>
  );
}

export function LoadingButton({
  isLoading,
  children,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { isLoading: boolean }) {
  return (
    <button
      {...props}
      disabled={isLoading || props.disabled}
      className={cn(
        'inline-flex items-center justify-center gap-2 px-4 py-2 rounded-md font-medium transition-colors',
        'bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed',
        props.className
      )}
    >
      {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
      {children}
    </button>
  );
}
