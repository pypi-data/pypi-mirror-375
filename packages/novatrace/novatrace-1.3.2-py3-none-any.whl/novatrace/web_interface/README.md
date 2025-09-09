# NovaTrace Web Interface

Modern React-based web interface for NovaTrace system monitoring.

## Features

- 🎯 **Real-time Monitoring**: Live system metrics with auto-refresh
- 📊 **Interactive Dashboard**: Visual charts and metrics cards
- 🚀 **Project Management**: Monitor and control active projects
- ⚙️ **Configurable Settings**: Customize monitoring preferences
- 🎨 **Modern UI**: Built with React and Tailwind CSS
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Technology Stack

- **Frontend**: React 18
- **Styling**: Tailwind CSS
- **Build Tool**: Vite
- **Icons**: Lucide React
- **Routing**: React Router DOM

## Quick Start

### Prerequisites

- Node.js 16+ 
- npm or yarn

### Installation

1. Navigate to the web interface directory:
   ```bash
   cd web_interface
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser and visit: `http://localhost:3000`

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Layout.jsx      # Main layout wrapper
│   ├── MetricCard.jsx  # System metric cards
│   ├── RecentProjects.jsx
│   └── SystemChart.jsx # Chart components
├── pages/              # Page components
│   ├── Dashboard.jsx   # Main dashboard
│   ├── Projects.jsx    # Project management
│   └── Settings.jsx    # Configuration
├── App.jsx            # Main app component
├── main.jsx           # Entry point
└── index.css          # Global styles
```

## Features Overview

### Dashboard
- Real-time system metrics (CPU, Memory, Disk, Network)
- Interactive charts showing historical data
- Recent projects overview
- System status information

### Projects
- View all monitored projects
- Start/stop/pause project controls
- Resource usage monitoring
- Search and filter capabilities

### Settings
- Configure monitoring intervals
- Set alert thresholds
- Customize notifications
- Manage data retention

## API Integration

The interface is designed to work with the NovaTrace Python backend. Configure the API endpoint in `vite.config.js`:

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

## Customization

### Styling
- Edit `tailwind.config.js` for theme customization
- Modify component styles in individual files
- Global styles in `src/index.css`

### Components
- All components are modular and reusable
- Easy to extend with new features
- Consistent design patterns

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of NovaTrace and follows the same license terms.
