import { format, differenceInDays } from 'date-fns';

export const formatDate = (date: Date): string => {
  return format(date, 'MMM d, yyyy');
};

export const formatDateShort = (date: Date): string => {
  return format(date, 'MMM d');
};

export const formatTime = (time: string): string => {
  const [hours, minutes] = time.split(':');
  const hour = parseInt(hours, 10);
  const ampm = hour >= 12 ? 'PM' : 'AM';
  const displayHour = hour % 12 || 12;
  return `${displayHour}:${minutes} ${ampm}`;
};

export const calculateTripDuration = (startDate: Date, endDate: Date): number => {
  return differenceInDays(endDate, startDate) + 1;
};

export const getDayNumber = (startDate: Date, currentDate: Date): number => {
  return differenceInDays(currentDate, startDate) + 1;
};