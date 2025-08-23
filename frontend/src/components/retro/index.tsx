import React from 'react';
import { X, Minus, Square } from 'lucide-react';

export const theme = {
  colors: {
    canvas: 'bg-[#F9F4ED]',
    surface: 'bg-white',
    ink: 'text-[#222222] border-[#222222]',
    inkWeak: 'text-[#4E4E4E]',
    blue: 'bg-[#4A90E2] text-white',
    green: 'bg-[#6FCF97] text-white',
    orange: 'bg-[#F5A25D] text-white',
    yellow: 'bg-[#F5D547] text-black',
    red: 'bg-[#E94F37] text-white',
    muted: 'bg-[#ECE7DF] border-[#ECE7DF]',
  }
};

interface RetroWindowProps {
  variant?: 'default' | 'flight' | 'hotel' | 'meal' | 'error' | 'assistant';
  title: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
  onClose?: () => void;
  className?: string;
}

export const RetroWindow: React.FC<RetroWindowProps> = ({ 
  variant = 'default', 
  title, 
  icon, 
  children, 
  onClose, 
  className = '' 
}) => {
  const variantStyles = {
    default: 'bg-gray-400',
    flight: theme.colors.blue,
    hotel: theme.colors.green,
    meal: theme.colors.orange,
    error: theme.colors.red,
    assistant: 'bg-purple-400 text-white'
  };

  return (
    <div className={`${theme.colors.surface} border-2 ${theme.colors.ink} rounded-[10px] shadow-[0_4px_0_0_#222222] ${className}`}>
      <div className={`${variantStyles[variant]} px-3 py-2 rounded-t-[8px] flex items-center justify-between border-b-2 border-[#222222]`}>
        <div className="flex items-center gap-2">
          {icon && <span className="w-4 h-4">{icon}</span>}
          <span className="font-semibold text-sm">{title}</span>
        </div>
        <div className="flex gap-1">
          <button className="w-5 h-5 bg-yellow-400 border border-black rounded-sm flex items-center justify-center hover:bg-yellow-500">
            <Minus className="w-3 h-3" />
          </button>
          <button className="w-5 h-5 bg-green-400 border border-black rounded-sm flex items-center justify-center hover:bg-green-500">
            <Square className="w-2 h-2" />
          </button>
          {onClose && (
            <button onClick={onClose} className="w-5 h-5 bg-red-400 border border-black rounded-sm flex items-center justify-center hover:bg-red-500">
              <X className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>
      <div className="p-4">{children}</div>
    </div>
  );
};

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost';
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
  type?: 'button' | 'submit' | 'reset';
}

export const Button: React.FC<ButtonProps> = ({ 
  variant = 'primary', 
  children, 
  onClick, 
  disabled, 
  className = '',
  type = 'button'
}) => {
  const variants = {
    primary: `${theme.colors.blue} border-2 border-[#222222] shadow-[0_2px_0_0_#222222] hover:shadow-[0_1px_0_0_#222222] hover:translate-y-[1px]`,
    secondary: `${theme.colors.surface} ${theme.colors.ink} border-2 border-[#222222] shadow-[0_2px_0_0_#222222] hover:shadow-[0_1px_0_0_#222222] hover:translate-y-[1px]`,
    ghost: 'hover:bg-gray-100'
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`px-4 py-2 rounded-[8px] font-medium transition-all duration-120 disabled:opacity-50 ${variants[variant]} ${className}`}
    >
      {children}
    </button>
  );
};

interface InputProps {
  label?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  type?: string;
  className?: string;
  name?: string;
  required?: boolean;
}

export const Input: React.FC<InputProps> = ({ 
  label, 
  value, 
  onChange, 
  placeholder, 
  type = 'text', 
  className = '',
  name,
  required
}) => (
  <div className="space-y-1">
    {label && <label className="text-sm font-medium">{label}</label>}
    <input
      type={type}
      name={name}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      required={required}
      className={`w-full px-3 py-2 border-2 border-[#222222] rounded-[8px] bg-white shadow-inner focus:outline-none focus:ring-2 focus:ring-[#4A90E280] ${className}`}
    />
  </div>
);

interface SelectProps {
  label?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  options: { value: string; label: string }[];
  className?: string;
  name?: string;
  required?: boolean;
}

export const Select: React.FC<SelectProps> = ({ 
  label, 
  value, 
  onChange, 
  options, 
  className = '',
  name,
  required
}) => (
  <div className="space-y-1">
    {label && <label className="text-sm font-medium">{label}</label>}
    <select
      name={name}
      value={value}
      onChange={onChange}
      required={required}
      className={`w-full px-3 py-2 border-2 border-[#222222] rounded-[8px] bg-white shadow-inner focus:outline-none focus:ring-2 focus:ring-[#4A90E280] ${className}`}
    >
      {options.map(opt => (
        <option key={opt.value} value={opt.value}>{opt.label}</option>
      ))}
    </select>
  </div>
);

interface TagProps {
  selected: boolean;
  children: React.ReactNode;
  onClick: () => void;
}

export const Tag: React.FC<TagProps> = ({ selected, children, onClick }) => (
  <button
    type="button"
    onClick={onClick}
    className={`px-3 py-1 rounded-full border-2 border-[#222222] text-sm font-medium transition-all ${
      selected ? 'bg-[#4A90E2] text-white' : 'bg-white hover:bg-gray-50'
    }`}
  >
    {children}
  </button>
);

interface ProgressBarProps {
  progress: number;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ progress }) => {
  const segments = 12;
  const filled = Math.floor((progress / 100) * segments);
  
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 bg-white border-2 border-[#222222] rounded-[8px] p-2">
        <div className="flex gap-1">
          {[...Array(segments)].map((_, i) => (
            <div
              key={i}
              className={`flex-1 h-4 rounded-sm transition-all duration-[60ms] ${
                i < filled ? 'bg-[#4A90E2]' : 'bg-gray-200'
              }`}
            />
          ))}
        </div>
      </div>
      <span className="font-mono text-sm font-bold">{progress}%</span>
    </div>
  );
};

export { DayTabs } from './DayTabs';