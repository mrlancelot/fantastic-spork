import { ExternalLink, Phone, MessageCircle } from 'lucide-react';
import { Button } from './Button';

const platformColors = {
  'Google Flights': 'bg-blue-600 hover:bg-blue-700',
  'Booking.com': 'bg-blue-700 hover:bg-blue-800',
  'Airbnb': 'bg-red-500 hover:bg-red-600',
  'OpenTable': 'bg-red-600 hover:bg-red-700',
  'Viator': 'bg-orange-500 hover:bg-orange-600',
  'GetYourGuide': 'bg-orange-600 hover:bg-orange-700',
  'WhatsApp': 'bg-green-500 hover:bg-green-600',
  'Direct': 'bg-gray-700 hover:bg-gray-800',
  'Phone': 'bg-purple-600 hover:bg-purple-700',
};

export function BookingButton({ option, className = "" }) {
  const { platform, url, contact, price_range, price_per_person, price_per_night, notes } = option;
  
  const getButtonColor = (platform) => {
    return platformColors[platform] || 'bg-blue-600 hover:bg-blue-700';
  };
  
  const getIcon = () => {
    if (platform === 'WhatsApp') return <MessageCircle className="w-4 h-4" />;
    if (platform === 'Phone' || contact?.startsWith('+')) return <Phone className="w-4 h-4" />;
    return <ExternalLink className="w-4 h-4" />;
  };
  
  const getHref = () => {
    if (url) return url;
    if (platform === 'WhatsApp' && contact) {
      // Format WhatsApp link
      const cleanNumber = contact.replace(/[^\d]/g, '');
      return `https://wa.me/${cleanNumber}`;
    }
    if (contact?.startsWith('+')) {
      return `tel:${contact}`;
    }
    return '#';
  };
  
  const displayPrice = price_range || price_per_person || price_per_night;
  
  return (
    <div className={`space-y-2 ${className}`}>
      <Button
        asChild
        className={`w-full text-white ${getButtonColor(platform)} transition-colors`}
        size="sm"
      >
        <a
          href={getHref()}
          target={url ? "_blank" : "_self"}
          rel={url ? "noopener noreferrer" : undefined}
          className="flex items-center justify-between"
        >
          <div className="flex items-center gap-2">
            {getIcon()}
            <span className="font-medium">{platform}</span>
          </div>
          {displayPrice && (
            <span className="text-sm opacity-90">{displayPrice}</span>
          )}
        </a>
      </Button>
      
      {notes && (
        <p className="text-xs text-gray-600 px-2">{notes}</p>
      )}
      
      {contact && platform !== 'WhatsApp' && platform !== 'Phone' && (
        <div className="flex items-center gap-1 px-2">
          <Phone className="w-3 h-3 text-gray-500" />
          <a 
            href={`tel:${contact}`}
            className="text-xs text-gray-600 hover:text-gray-800"
          >
            {contact}
          </a>
        </div>
      )}
    </div>
  );
}