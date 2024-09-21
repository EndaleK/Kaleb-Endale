'use client';  // Add this line at the top of the file

import React, { useState, useEffect } from 'react';
import { UserButton } from "@clerk/nextjs";
import { Moon, Sun, Palette } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [darkMode, setDarkMode] = useState(false);
  const [grayBackground, setGrayBackground] = useState(false);

  useEffect(() => {
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    const isGrayBackground = localStorage.getItem('grayBackground') === 'true';
    setDarkMode(isDarkMode);
    setGrayBackground(isGrayBackground);
    document.documentElement.classList.toggle('dark', isDarkMode);
    document.documentElement.classList.toggle('gray-bg', isGrayBackground);
  }, []);

  const toggleDarkMode = () => {
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    localStorage.setItem('darkMode', newDarkMode.toString());
    document.documentElement.classList.toggle('dark', newDarkMode);
  };

  const toggleGrayBackground = () => {
    const newGrayBackground = !grayBackground;
    setGrayBackground(newGrayBackground);
    localStorage.setItem('grayBackground', newGrayBackground.toString());
    document.documentElement.classList.toggle('gray-bg', newGrayBackground);
  };

  return (
    <div className="layout-container">
      <header className="header">
        <div>FamSync</div>
        <div className="flex items-center space-x-4">
          <button 
            onClick={toggleGrayBackground} 
            className="p-2 rounded-full hover:bg-opacity-20 hover:bg-gray-200 dark:hover:bg-gray-700"
            aria-label="Toggle gray background"
          >
            <Palette size={20} />
          </button>
          <button 
            onClick={toggleDarkMode} 
            className="p-2 rounded-full hover:bg-opacity-20 hover:bg-gray-200 dark:hover:bg-gray-700"
            aria-label={darkMode ? "Switch to light mode" : "Switch to dark mode"}
          >
            {darkMode ? <Sun size={20} /> : <Moon size={20} />}
          </button>
          <UserButton afterSignOutUrl="/"/>
        </div>
      </header>
      <main className="main-content">
        <h1 className="calendar-title">Family Calendar</h1>
        {children}
      </main>
    </div>
  );
};

export default Layout;