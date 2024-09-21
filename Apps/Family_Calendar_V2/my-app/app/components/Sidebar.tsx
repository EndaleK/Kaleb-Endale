'use client';

import React from 'react';
import { Plus, Trash2, Calendar, Palette } from 'lucide-react';
import styles from '../styles/Sidebar.module.css';
import ThemeSelector from './ThemeSelector';
import { useTheme } from '../ThemeContext';
import Weather from './Weather';
import MiniCalendar from './MiniCalendar';
import DailyQuote from './DailyQuote';

interface Event {
  id: string;
  title: string;
  date: Date;
  time: string;
  familyMember: string;
}

interface SidebarProps {
  familyMembers: string[];
  onAddFamilyMember: (name: string) => void;
  onRemoveFamilyMember: (name: string) => void;
  familyMemberColors: Record<string, string>;
  upcomingEvents: Event[];
}

const Sidebar: React.FC<SidebarProps> = ({
  familyMembers,
  onAddFamilyMember,
  onRemoveFamilyMember,
  familyMemberColors,
  upcomingEvents,
}) => {
  const [newMember, setNewMember] = React.useState('');
  const { theme } = useTheme();

  const handleAddMember = () => {
    if (newMember.trim()) {
      onAddFamilyMember(newMember.trim());
      setNewMember('');
    }
  };

  return (
    <div className={`${styles.sidebar} theme-${theme}`}>
      <Weather />
      
      <div className={styles.section}>
        <MiniCalendar />
      </div>
      
      <div className={styles.section}>
        <DailyQuote />
      </div>
      
      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>
          <Calendar size={18} className={styles.icon} />
          Upcoming Events
        </h3>
        <ul className={styles.eventList}>
          {upcomingEvents.map((event) => (
            <li key={event.id} className={styles.eventItem}>
              <span style={{ backgroundColor: familyMemberColors[event.familyMember] }} className={styles.eventColor}></span>
              <div className={styles.eventInfo}>
                <span className={styles.eventTitle}>{event.title}</span>
                <span className={styles.eventDate}>{event.date.toLocaleDateString()} - {event.time}</span>
                <span className={styles.eventMember}>{event.familyMember}</span>
              </div>
            </li>
          ))}
        </ul>
      </div>

      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>
          <Plus size={18} className={styles.icon} />
          Family Members
        </h3>
        <ul className={styles.familyList}>
          {familyMembers.map((member) => (
            <li key={member} className={styles.familyMember}>
              <span style={{ backgroundColor: familyMemberColors[member] }} className={styles.memberColor}></span>
              {member}
              <button onClick={() => onRemoveFamilyMember(member)} className={styles.removeButton}>
                <Trash2 size={16} />
              </button>
            </li>
          ))}
        </ul>
        <div className={styles.addMember}>
          <input
            type="text"
            value={newMember}
            onChange={(e) => setNewMember(e.target.value)}
            placeholder="New member name"
            className={styles.addMemberInput}
          />
          <button onClick={handleAddMember} className={styles.addButton}>
            <Plus size={16} />
          </button>
        </div>
      </div>

      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>
          <Palette size={18} className={styles.icon} />
          Theme
        </h3>
        <ThemeSelector />
      </div>
    </div>
  );
};

export default Sidebar;