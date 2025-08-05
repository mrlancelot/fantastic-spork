import { Phone, MessageCircle, ExternalLink } from 'lucide-react';

export function ContactInfo({ contact, platform, notes, className = "" }) {
  if (!contact) return null;
  
  const isWhatsApp = platform === 'WhatsApp' || contact.toLowerCase().includes('whatsapp');
  const isPhone = contact.startsWith('+') || /^\d/.test(contact);
  
  const getWhatsAppLink = (number) => {
    const cleanNumber = number.replace(/[^\d]/g, '');
    return `https://wa.me/${cleanNumber}`;
  };
  
  return (
    <div className={`flex items-center gap-2 text-sm ${className}`}>
      {isWhatsApp ? (
        <a
          href={getWhatsAppLink(contact)}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 text-green-600 hover:text-green-700"
        >
          <MessageCircle className="w-4 h-4" />
          <span>WhatsApp: {contact}</span>
          <ExternalLink className="w-3 h-3" />
        </a>
      ) : isPhone ? (
        <a
          href={`tel:${contact}`}
          className="flex items-center gap-1 text-purple-600 hover:text-purple-700"
        >
          <Phone className="w-4 h-4" />
          <span>{contact}</span>
        </a>
      ) : (
        <div className="flex items-center gap-1 text-gray-600">
          <span>{contact}</span>
        </div>
      )}
      
      {notes && (
        <span className="text-xs text-gray-500 ml-2">({notes})</span>
      )}
    </div>
  );
}