import React, { useState, useEffect } from 'react';

interface WeatherData {
  location: {
    name: string;
    region: string;
  };
  current: {
    temp_c: number;
    condition: {
      text: string;
      icon: string;
    };
  };
}

const Weather: React.FC = () => {
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWeather = async () => {
      try {
        const response = await fetch(`https://api.weatherapi.com/v1/current.json?key=${process.env.NEXT_PUBLIC_WEATHER_API_KEY}&q=auto:ip`);
        if (!response.ok) {
          throw new Error('Failed to fetch weather data');
        }
        const data: WeatherData = await response.json();
        setWeatherData(data);
        setLoading(false);
      } catch (err) {
        setError('Error fetching weather data');
        setLoading(false);
      }
    };

    fetchWeather();
  }, []);

  if (loading) return <div>Loading weather...</div>;
  if (error) return <div>{error}</div>;
  if (!weatherData) return null;

  return (
    <div className="weather-container">
      <h2>{weatherData.location.name}, {weatherData.location.region}</h2>
      <div className="weather-info">
        <img src={weatherData.current.condition.icon} alt={weatherData.current.condition.text} />
        <p>{weatherData.current.temp_c}°C</p>
        <p>{weatherData.current.condition.text}</p>
      </div>
    </div>
  );
};

export default Weather;