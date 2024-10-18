'use client';

import React, { useState, useEffect } from 'react';
import { format, addMonths, subMonths, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, isToday, addDays } from 'date-fns';
import { ChevronLeft, ChevronRight, Search, Plus } from 'lucide-react';
import Sidebar from './Sidebar';
import AddEventModal from './AddEventModal';
import MiniCalendar from './MiniCalendar';
import { v4 as uuidv4 } from 'uuid';
import styles from '../styles/Calendar.module.css';
import Weather from './Weather'; // New component for weather

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

const colorPalette = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
  '#F06292', '#AED581', '#7986CB', '#4DB6AC', '#FFD54F'
];

const Calendar: React.FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [events, setEvents] = useState<Event[]>([]);
  const [isAddEventModalOpen, setIsAddEventModalOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [familyMembers, setFamilyMembers] = useState<string[]>(['Mom', 'Dad', 'Sister', 'Brother']);
  const [familyMemberColors, setFamilyMemberColors] = useState<Record<string, string>>({});
  const [appBackgroundColor, setAppBackgroundColor] = useState('#ffffff');
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
  const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay();

  const assignColorToFamilyMember = (name: string) => {
    if (!familyMemberColors[name]) {
      const availableColors = colorPalette.filter(color => !Object.values(familyMemberColors).includes(color));
      const newColor = availableColors[Math.floor(Math.random() * availableColors.length)] || colorPalette[0];
      setFamilyMemberColors(prev => ({ ...prev, [name]: newColor }));
    }
  };

  const handleAddFamilyMember = (name: string) => {
    setFamilyMembers([...familyMembers, name]);
    assignColorToFamilyMember(name);
  };

  const handleRemoveFamilyMember = (name: string) => {
    setFamilyMembers(familyMembers.filter(member => member !== name));
    setFamilyMemberColors(prev => {
      const { [name]: _, ...rest } = prev;
      return rest;
    });
  };

  const isToday = (date: Date) => {
    const today = new Date();
    return date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear();
  };

  const generateRecurringEvents = (event: Event): Event[] => {
    const recurringEvents: Event[] = [];
    const endDate = new Date(currentDate);
    endDate.setMonth(endDate.getMonth() + 1);

    let currentEventDate = new Date(event.date);

    while (currentEventDate <= endDate) {
      recurringEvents.push({
        ...event,
        date: new Date(currentEventDate),
        id: `${event.id}-${currentEventDate.toISOString()}`
      });

      switch (event.recurrenceType) {
        case 'daily':
          currentEventDate.setDate(currentEventDate.getDate() + 1);
          break;
        case 'weekly':
          currentEventDate.setDate(currentEventDate.getDate() + 7);
          break;
        case 'monthly':
          currentEventDate.setMonth(currentEventDate.getMonth() + 1);
          break;
      }
    }

    return recurringEvents;
  };

  const renderCalendarDays = () => {
    const days = [];
    for (let i = 0; i < firstDayOfMonth; i++) {
      days.push(<div key={`empty-${i}`} className="calendar-day empty"></div>);
    }

    const allEvents = events.flatMap(event => 
      event.isRecurring ? generateRecurringEvents(event) : [event]
    );

    for (let i = 1; i <= daysInMonth; i++) {
      const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), i);
      const dayEvents = allEvents.filter(event => event.date.toDateString() === date.toDateString());
      
      const maxVisibleEvents = 3; // Revert to showing 3 events
      const visibleEvents = dayEvents.slice(0, maxVisibleEvents);
      const hiddenEventsCount = dayEvents.length - maxVisibleEvents;

      const isTodayDate = isToday(date);
      const isWeekend = date.getDay() === 0 || date.getDay() === 6; // 0 is Sunday, 6 is Saturday
      
      days.push(
        <div 
          key={i} 
          className={`calendar-day ${isTodayDate ? 'today' : ''} ${isWeekend ? 'weekend' : ''}`} 
          onClick={() => handleDayClick(date)}
        >
          <span className={`day-number ${isTodayDate ? 'today-number' : ''}`}>{i}</span>
          <div className="event-container">
            {visibleEvents.map((event, index) => (
              <div
                key={index}
                className="event-indicator"
                style={{ 
                  backgroundColor: event.familyMember === 'Everyone' 
                    ? 'var(--accent-color)' 
                    : familyMemberColors[event.familyMember] || '#4a90e2' 
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedEvent(event);
                  setIsAddEventModalOpen(true);
                }}
                title={`${event.title} - ${event.time} - ${event.familyMember}`}
              >
                {event.time} - {event.title}
              </div>
            ))}
            {hiddenEventsCount > 0 && (
              <div className="text-[10px] text-gray-500 mt-0.5">
                +{hiddenEventsCount} more
              </div>
            )}
          </div>
        </div>
      );
    }
    return days;
  };

  const prevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const handleDayClick = (date: Date) => {
    setSelectedDate(date);
    setIsAddEventModalOpen(true);
  };

  const handleAddEvent = (newEvent: Omit<Event, 'id'>) => {
    const eventWithId = { ...newEvent, id: uuidv4() };
    setEvents([...events, eventWithId]);
  };

  const handleDeleteEvent = (id: string) => {
    setEvents(events.filter(event => event.id !== id));
  };

  const handleMiniCalendarDateChange = (date: Date) => {
    setCurrentDate(date);
  };

  const getUpcomingEvents = () => {
    const today = new Date();
    const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
    return events
      .filter(event => event.date >= today && event.date <= nextWeek)
      .sort((a, b) => a.date.getTime() - b.date.getTime())
      .slice(0, 5); // Get top 5 upcoming events
  };

  const handleBackgroundColorChange = (color: string) => {
    setAppBackgroundColor(color);
  };

  const handleThemeChange = (newTheme: 'light' | 'dark') => {
    setTheme(newTheme);
    document.documentElement.classList.toggle('dark', newTheme === 'dark');
  };

  useEffect(() => {
    // Initialize theme based on user preference or system setting
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    handleThemeChange(prefersDark ? 'dark' : 'light');
  }, []);

  return (
    <div className={`app-container ${theme}`}>
      <div className="calendar-container">
        <Sidebar
          familyMembers={familyMembers}
          onAddFamilyMember={handleAddFamilyMember}
          onRemoveFamilyMember={handleRemoveFamilyMember}
          familyMemberColors={familyMemberColors}
          events={events}
          onDeleteEvent={handleDeleteEvent}
          upcomingEvents={getUpcomingEvents()}
          onThemeChange={handleThemeChange}
          currentTheme={theme}
          onBackgroundColorChange={handleBackgroundColorChange} // Add this line
        >
          <Weather />
          <MiniCalendar
            currentDate={currentDate}
            onDateChange={handleMiniCalendarDateChange}
            events={events}
          />
        </Sidebar>
        <div className="calendar-main">
          <div className="calendar-header flex justify-between items-center py-4 px-4">
            <button onClick={prevMonth} className="nav-button">
              <ChevronLeft size={24} />
            </button>
            <h2 className="text-2xl font-semibold">
              {currentDate.toLocaleString('default', { month: 'long', year: 'numeric' })}
            </h2>
            <button onClick={nextMonth} className="nav-button">
              <ChevronRight size={24} />
            </button>
          </div>
          <div className="days-of-week">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
              <div key={day} className="day-name">{day}</div>
            ))}
          </div>
          <div className="calendar-grid-wrapper">
            <div className="calendar-grid">
              {renderCalendarDays()}
            </div>
          </div>
        </div>
      </div>
      <AddEventModal
        isOpen={isAddEventModalOpen}
        onClose={() => {
          setIsAddEventModalOpen(false);
          setSelectedEvent(null);
        }}
        onAddEvent={handleAddEvent}
        selectedDate={selectedDate}
        selectedEvent={selectedEvent}
        familyMembers={familyMembers}
      />
    </div>
  );
};

export default Calendar;