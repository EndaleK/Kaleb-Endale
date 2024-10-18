'use client';

import React from 'react';
import { Trash2 } from 'lucide-react';

interface FamilyMembersProps {
  members: string[];
  onAddMember: (name: string) => void;
  onRemoveMember: (name: string) => void;
  memberColors: Record<string, string>;
}

const FamilyMembers: React.FC<FamilyMembersProps> = ({ members, onAddMember, onRemoveMember, memberColors }) => {
  const [newMember, setNewMember] = React.useState('');

  const handleAddMember = () => {
    if (newMember.trim()) {
      onAddMember(newMember.trim());
      setNewMember('');
    }
  };

  return (
    <div>
      <ul className="space-y-2 mb-4">
        {members.map((member) => (
          <li key={member} className="flex items-center justify-between text-sm bg-[var(--calendar-bg)] rounded-md p-2 shadow-sm">
            <span className="flex items-center">
              <span 
                className="w-4 h-4 rounded-full mr-2" 
                style={{ backgroundColor: memberColors[member] || '#4a90e2' }}
              ></span>
              {member}
            </span>
            <button
              onClick={() => onRemoveMember(member)}
              className="text-gray-400 hover:text-red-500 transition-colors duration-200"
              aria-label={`Remove ${member}`}
            >
              <Trash2 size={16} />
            </button>
          </li>
        ))}
      </ul>
      <div className="flex">
        <input
          type="text"
          value={newMember}
          onChange={(e) => setNewMember(e.target.value)}
          className="text-sm border rounded-l px-2 py-1 w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Add family member"
        />
        <button
          onClick={handleAddMember}
          className="bg-blue-500 text-white rounded-r px-3 py-1 text-sm hover:bg-blue-600 transition-colors duration-200"
        >
          Add
        </button>
      </div>
    </div>
  );
};

export default FamilyMembers;