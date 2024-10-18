import React from 'react';
import { isToday, isFuture, format } from 'date-fns';
import { Trash2 } from 'lucide-react';

interface Event {
  id: string;
  title: string;
  date: Date;
  time: string;
  description: string;
  familyMember: string;
}

interface UpcomingEventsProps {
  events: Event[];
  onDeleteEvent: (id: string) => void;
  familyMemberColors: Record<string, string>;
}

const eventColors: Record<string, string> = {
  'Birthday': '#FF6B6B',
  'Anniversary': '#4ECDC4',
  'School Event': '#45B7D1',
  'Holiday Celebration': '#FFA07A',
  'Family Reunion': '#98D8C8',
  'Wedding': '#F06292',
  'Graduation': '#AED581',
  'Religious Service/Event': '#7986CB',
  'Community Festival': '#4DB6AC',
  'Vacation': '#FFD54F',
  'Doctor/Dentist Appointment': '#FF8A65',
  'Sports Practice/Game': '#81C784',
  'Music/Dance Recital': '#9575CD',
  'Parent-Child Activity': '#4DD0E1',
  'Work-Related Event': '#A1887F',
  'Neighborhood Gathering': '#DCE775',
  'Movie Night': '#BA68C8',
  'Seasonal Activity': '#4FC3F7',
  'School Field Trip': '#FFF176',
  'Charity Event/Volunteering': '#F06292',
  'Other': '#90A4AE'
};

const UpcomingEvents: React.FC<UpcomingEventsProps> = ({ events = [], onDeleteEvent, familyMemberColors }) => {
  const sortedEvents = events && events.length > 0
    ? events
        .filter(event => isToday(new Date(event.date)) || isFuture(new Date(event.date)))
        .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
        .slice(0, 5)
    : [];

  const getEventColor = (event: Event) => {
    if (event.familyMember === 'Everyone') {
      return 'var(--accent-color)';
    }
    return eventColors[event.title] || familyMemberColors[event.familyMember] || '#90A4AE';
  };

  return (
    <div className="upcoming-events">
      <ul className="space-y-2">
        {sortedEvents.map(event => (
          <li key={event.id} className="flex items-center justify-between bg-white p-2 rounded-md shadow-sm">
            <div className="flex items-center space-x-2">
              <div
                className="w-3 h-3 rounded-full flex-shrink-0"
                style={{ backgroundColor: getEventColor(event) }}
              ></div>
              <div>
                <p className="text-sm font-medium">{event.title}</p>
                <p className="text-xs text-gray-500">
                  {format(new Date(event.date), 'MMM d, yyyy')} - {event.time}
                </p>
                <p className="text-xs text-gray-500">
                  {event.familyMember === 'Everyone' ? 'Everyone' : event.familyMember}
                </p>
              </div>
            </div>
            <button
              onClick={() => onDeleteEvent(event.id)}
              className="text-gray-400 hover:text-red-500 transition-colors duration-200"
              aria-label="Delete event"
            >
              <Trash2 size={16} />
            </button>
          </li>
        ))}
      </ul>
      {sortedEvents.length === 0 && (
        <p className="text-sm text-gray-500">No upcoming events</p>
      )}
    </div>
  );
};

export default UpcomingEvents;