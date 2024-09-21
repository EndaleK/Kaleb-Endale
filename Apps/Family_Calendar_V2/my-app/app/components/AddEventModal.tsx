import React, { useState, useEffect } from 'react';
import { Clock } from 'lucide-react';

interface Event {
  id: string;
  title: string;
  date: Date;
  time: string;
  description: string;
  familyMember: string;
  isRecurring: boolean;
  recurrenceType?: 'daily' | 'weekly' | 'monthly';
}

interface AddEventModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAddEvent: (event: Event) => void;
  selectedDate: Date;
  selectedEvent: Event | null;
  familyMembers: string[];
}

const eventTitles = [
  'Birthday',
  'Anniversary',
  'School Event',
  'Holiday Celebration',
  'Family Reunion',
  'Wedding',
  'Graduation',
  'Religious Service/Event',
  'Community Festival',
  'Vacation',
  'Doctor/Dentist Appointment',
  'Sports Practice/Game',
  'Music/Dance Recital',
  'Parent-Child Activity',
  'Work-Related Event',
  'Neighborhood Gathering',
  'Movie Night',
  'Seasonal Activity',
  'School Field Trip',
  'Charity Event/Volunteering',
  'Other'
];

const AddEventModal: React.FC<AddEventModalProps> = ({ isOpen, onClose, onAddEvent, selectedDate, selectedEvent, familyMembers }) => {
  const [title, setTitle] = useState('');
  const [customTitle, setCustomTitle] = useState('');
  const [hours, setHours] = useState('12');
  const [minutes, setMinutes] = useState('00');
  const [description, setDescription] = useState('');
  const [familyMember, setFamilyMember] = useState('');
  const [isRecurring, setIsRecurring] = useState(false);
  const [recurrenceType, setRecurrenceType] = useState<'daily' | 'weekly' | 'monthly'>('daily');

  useEffect(() => {
    if (selectedEvent) {
      setTitle(selectedEvent.title);
      setCustomTitle(eventTitles.includes(selectedEvent.title) ? '' : selectedEvent.title);
      const [eventHours, eventMinutes] = selectedEvent.time.split(':');
      setHours(eventHours);
      setMinutes(eventMinutes);
      setDescription(selectedEvent.description);
      setFamilyMember(selectedEvent.familyMember);
      setIsRecurring(selectedEvent.isRecurring);
      setRecurrenceType(selectedEvent.recurrenceType || 'daily');
    } else {
      setTitle('');
      setCustomTitle('');
      setHours('12');
      setMinutes('00');
      setDescription('');
      setFamilyMember('');
      setIsRecurring(false);
      setRecurrenceType('daily');
    }
  }, [selectedEvent]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const finalTitle = title === 'Other' ? customTitle : title;
    const time = `${hours.padStart(2, '0')}:${minutes}`;
    onAddEvent({ 
      id: selectedEvent?.id || '', 
      title: finalTitle, 
      date: selectedDate, 
      time, 
      description, 
      familyMember: familyMember === 'Everyone' ? 'Everyone' : familyMember,
      isRecurring,
      recurrenceType: isRecurring ? recurrenceType : undefined
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-[var(--calendar-bg)] text-[var(--text-color)] p-6 rounded-lg shadow-lg w-96">
        <h2 className="text-xl font-bold mb-4">{selectedEvent ? 'Event Details' : 'Add New Event'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="title" className="block text-sm font-medium text-[var(--text-color)]">Title</label>
            <select
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="mt-1 block w-full rounded-md border-[var(--border-color)] bg-[var(--calendar-bg)] text-[var(--text-color)] shadow-sm focus:border-[var(--accent-color)] focus:ring focus:ring-[var(--accent-color)] focus:ring-opacity-50"
              required
            >
              <option value="">Select an event type</option>
              {eventTitles.map((eventTitle) => (
                <option key={eventTitle} value={eventTitle}>{eventTitle}</option>
              ))}
            </select>
            {title === 'Other' && (
              <input
                type="text"
                value={customTitle}
                onChange={(e) => setCustomTitle(e.target.value)}
                className="mt-2 block w-full rounded-md border-[var(--border-color)] bg-[var(--calendar-bg)] text-[var(--text-color)] shadow-sm focus:border-[var(--accent-color)] focus:ring focus:ring-[var(--accent-color)] focus:ring-opacity-50"
                placeholder="Enter custom event title"
                required
              />
            )}
          </div>
          <div className="mb-4">
            <label htmlFor="time" className="block text-sm font-medium text-[var(--text-color)]">Time</label>
            <div className="flex items-center mt-1">
              <select
                value={hours}
                onChange={(e) => setHours(e.target.value)}
                className="mr-2 rounded-md border-[var(--border-color)] bg-[var(--calendar-bg)] text-[var(--text-color)] shadow-sm focus:border-[var(--accent-color)] focus:ring focus:ring-[var(--accent-color)] focus:ring-opacity-50"
              >
                {Array.from({ length: 24 }, (_, i) => i).map((hour) => (
                  <option key={hour} value={hour.toString().padStart(2, '0')}>
                    {hour.toString().padStart(2, '0')}
                  </option>
                ))}
              </select>
              <span className="mr-2">:</span>
              <select
                value={minutes}
                onChange={(e) => setMinutes(e.target.value)}
                className="mr-2 rounded-md border-[var(--border-color)] bg-[var(--calendar-bg)] text-[var(--text-color)] shadow-sm focus:border-[var(--accent-color)] focus:ring focus:ring-[var(--accent-color)] focus:ring-opacity-50"
              >
                {['00', '15', '30', '45'].map((minute) => (
                  <option key={minute} value={minute}>{minute}</option>
                ))}
              </select>
              <Clock size={16} className="text-[var(--text-color)]" />
            </div>
          </div>
          <div className="mb-4">
            <label htmlFor="familyMember" className="block text-sm font-medium text-[var(--text-color)]">Family Member</label>
            <select
              id="familyMember"
              value={familyMember}
              onChange={(e) => setFamilyMember(e.target.value)}
              className="mt-1 block w-full rounded-md border-[var(--border-color)] bg-[var(--calendar-bg)] text-[var(--text-color)] shadow-sm focus:border-[var(--accent-color)] focus:ring focus:ring-[var(--accent-color)] focus:ring-opacity-50"
              required
            >
              <option value="">Select a family member</option>
              <option value="Everyone">Everyone</option>
              {familyMembers.map((member) => (
                <option key={member} value={member}>{member}</option>
              ))}
            </select>
          </div>
          <div className="mb-4">
            <label htmlFor="description" className="block text-sm font-medium text-[var(--text-color)]">Description</label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="mt-1 block w-full rounded-md border-[var(--border-color)] bg-[var(--calendar-bg)] text-[var(--text-color)] shadow-sm focus:border-[var(--accent-color)] focus:ring focus:ring-[var(--accent-color)] focus:ring-opacity-50"
              rows={3}
            ></textarea>
          </div>
          <div className="mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={isRecurring}
                onChange={(e) => setIsRecurring(e.target.checked)}
                className="mr-2"
              />
              <span className="text-sm font-medium text-[var(--text-color)]">Recurring Event</span>
            </label>
          </div>
          
          {isRecurring && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-[var(--text-color)] mb-2">Recurrence Type</label>
              <div className="flex space-x-4">
                {['daily', 'weekly', 'monthly'].map((type) => (
                  <label key={type} className="flex items-center">
                    <input
                      type="radio"
                      value={type}
                      checked={recurrenceType === type}
                      onChange={(e) => setRecurrenceType(e.target.value as 'daily' | 'weekly' | 'monthly')}
                      className="mr-2"
                    />
                    <span className="text-sm">{type.charAt(0).toUpperCase() + type.slice(1)}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          <div className="flex justify-end">
            <button type="button" onClick={onClose} className="mr-2 px-4 py-2 text-sm font-medium text-[var(--text-color)] bg-[var(--day-hover)] rounded-md hover:bg-opacity-80 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-[var(--accent-color)]">
              Close
            </button>
            <button type="submit" className="px-4 py-2 text-sm font-medium text-white bg-[var(--accent-color)] rounded-md hover:bg-opacity-80 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-[var(--accent-color)]">
              {selectedEvent ? 'Update Event' : 'Add Event'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddEventModal;