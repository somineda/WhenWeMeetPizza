import { ButtonHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'gradient';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      isLoading = false,
      disabled,
      children,
      ...props
    },
    ref
  ) => {
    const baseStyles =
      'inline-flex items-center justify-center font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none active:scale-[0.98]';

    const variants = {
      primary:
        'bg-primary-500 text-white rounded-xl hover:bg-primary-600 hover:shadow-soft hover:-translate-y-0.5 focus:ring-primary-500',
      secondary:
        'bg-gray-100 text-gray-900 rounded-xl hover:bg-gray-200 hover:shadow-soft hover:-translate-y-0.5 focus:ring-gray-400',
      outline:
        'border-2 border-primary-500 text-primary-600 rounded-xl hover:bg-primary-50 hover:shadow-soft hover:-translate-y-0.5 focus:ring-primary-500',
      ghost:
        'text-gray-700 rounded-xl hover:bg-gray-100 hover:text-gray-900 focus:ring-gray-400',
      danger:
        'bg-rose-500 text-white rounded-xl hover:bg-rose-600 hover:shadow-soft hover:-translate-y-0.5 focus:ring-rose-500',
      gradient:
        'bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-xl hover:from-primary-600 hover:to-primary-700 hover:shadow-glow hover:-translate-y-0.5 focus:ring-primary-500',
    };

    const sizes = {
      sm: 'px-4 py-2 text-sm gap-1.5',
      md: 'px-5 py-2.5 text-base gap-2',
      lg: 'px-7 py-3.5 text-lg gap-2.5',
    };

    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <>
            <svg
              className="animate-spin h-4 w-4"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            <span>처리 중...</span>
          </>
        ) : (
          children
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;
