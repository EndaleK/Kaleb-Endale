import React from 'react';
import { useTheme } from '../ThemeContext';

const ThemeSelector: React.FC = () => {
  const { theme, setTheme } = useTheme();

  return (
    <select
      value={theme}
      onChange={(e) => setTheme(e.target.value as any)}
      className="bg-transparent border border-gray-300 rounded px-2 py-1"
    >
      <option value="cherry-blossom">Cherry Blossom</option>
      <option value="ocean">Ocean</option>
      <option value="forest">Forest</option>
      <option value="sunset">Sunset</option>
    </select>
  );
};

export default ThemeSelector;