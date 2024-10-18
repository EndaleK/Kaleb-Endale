#Project overview
Use this guide to build interactive calendar that a family can use to schedule events, share responsibilities, and track tasks, and shopping list.

#feature requirements
1. **Family Sharing**: Ability to share calendars with family members and caregivers.
2. **Color-Coding**: Different colors for each family member's events and activities.
3. **Recurring Events**: Easy setup for recurring events like school pickups, sports practices, and music lessons.
4. **Reminders**: Customizable reminders and notifications to stay on track.
5. **Integrations**: Integration with other apps like school calendars, sports teams, and personal assistants.
6. **Task Management**: Ability to add tasks and to-do lists, with due dates and reminders.
7. **Notes and Comments**: Space for adding notes and comments to events and tasks.
8. **Drag-and-Drop**: Easy rescheduling of events using drag-and-drop functionality.
9. **Mobile Access**: Accessible on-the-go via mobile devices.
10. **Synchronization**: Automatic synchronization across all devices and family members' calendars.
11. **Birthday and Holiday Tracking**: Automatic tracking of birthdays and holidays.
12. **Weather Forecast**: Integration with weather forecasts to plan outdoor activities.
13. **School Schedule**: Integration with school schedules, including holidays and early dismissal days.
14. **Meal Planning**: Integration with meal planning apps or features to plan and organize meals.
15. **Self-Care**: Reminders and scheduling for self-care activities, like exercise or meditation.
16. we will use next js 14, tailwind css, shadcn/ui, and supabase for the database.
17. Have a dark theme. 
18. Have a light theme. 
19. Have a nice UI. 
20. Have a nice UX. 
21. Have a a weather forecast. 
22. Have a meal planning feature. 
22. Have a self-care feature. 

# Current File structure
project-root/
│
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── globals.css
│   │
│   ├── api/
│   │   └── ...
│   │
│   ├── components/
│   │   ├── ui/
│   │   │   └── ...
│   │   ├── Calendar.tsx
│   │   ├── EventForm.tsx
│   │   ├── TaskList.tsx
│   │   ├── WeatherWidget.tsx
│   │   ├── MealPlanner.tsx
│   │   └── SelfCareReminder.tsx
│   │
│   └── (routes)/
│       ├── calendar/
│       │   └── page.tsx
│       ├── tasks/
│       │   └── page.tsx
│       ├── meal-planning/
│       │   └── page.tsx
│       └── self-care/
│           └── page.tsx
│
├── lib/
│   ├── supabase.ts
│   └── utils.ts
│
├── styles/
│   └── theme.css
│
├── public/
│   └── ...
│
├── types/
│   └── index.ts
│
├── .env.local
├── next.config.js
├── package.json
├── tailwind.config.js
└── tsconfig.json

#Rules
- All new components should go in /components and be named like this: example-component.tsx unless otherwise specfied
- All new pages should go in /app/

#Relevant docs
