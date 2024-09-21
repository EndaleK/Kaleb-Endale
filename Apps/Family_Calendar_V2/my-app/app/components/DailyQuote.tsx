'use client';

import React, { useState, useEffect } from 'react';

const DailyQuote: React.FC = () => {
  const [quote, setQuote] = useState('');
  const [author, setAuthor] = useState('');

  useEffect(() => {
    const fetchQuote = async () => {
      try {
        const response = await fetch('https://api.quotable.io/random');
        const data = await response.json();
        setQuote(data.content);
        setAuthor(data.author);
      } catch (error) {
        console.error('Error fetching quote:', error);
        setQuote('The best preparation for tomorrow is doing your best today.');
        setAuthor('H. Jackson Brown Jr.');
      }
    };

    fetchQuote();
  }, []);

  return (
    <div className="daily-quote">
      <h3 className="text-lg font-semibold mb-2">Daily Quote</h3>
      <p className="italic">"{quote}"</p>
      <p className="text-right mt-2">- {author}</p>
    </div>
  );
};

export default DailyQuote;