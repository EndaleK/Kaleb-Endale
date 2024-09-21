'use client';

import React from 'react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isToday } from 'date-fns';

const MiniCalendar: React.FC = () => {
  const today = new Date();
  const start = startOfMonth(today);
  const end = endOfMonth(today);
  const days = eachDayOfInterval({ start, end });

  return (
    <div className="mini-calendar">
      <h3 className="text-lg font-semibold mb-2">{format(today, 'MMMM yyyy')}</h3>
      <div className="grid grid-cols-7 gap-1">
        {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map(day => (
          <div key={day} className="text-center text-xs font-medium">
            {day}
          </div>
        ))}
        {days.map(day => (
          <div
            key={day.toString()}
            className={`text-center text-sm p-1 ${
              !isSameMonth(day, today) ? 'text-gray-300' :
              isToday(day) ? 'bg-accent-color text-white rounded-full' : ''
            }`}
          >
            {format(day, 'd')}
          </div>
        ))}
      </div>
    </div>
  );
};

export default MiniCalendar;