import React from 'react'

const SystemChart = ({ title, data, color = 'blue', unit = '%' }) => {
  const colorClasses = {
    blue: 'stroke-blue-500',
    green: 'stroke-green-500',
    purple: 'stroke-purple-500',
    orange: 'stroke-orange-500',
  }

  // Simple line chart using SVG with proper margins for axes
  const maxValue = Math.max(...data)
  const minValue = Math.min(...data)
  const chartWidth = 280
  const chartHeight = 80
  const marginLeft = 40
  const marginBottom = 45
  
  const points = data.map((value, index) => {
    const x = marginLeft + (index / (data.length - 1)) * chartWidth
    const y = chartHeight - ((value - minValue) / (maxValue - minValue)) * chartHeight
    return `${x},${y}`
  }).join(' ')

  // Generate time labels (last 10 intervals)
  const timeLabels = data.map((_, index) => {
    const minutesAgo = (data.length - 1 - index) * 15 // 15 seconds intervals
    if (minutesAgo === 0) return 'Now'
    if (minutesAgo < 60) return `${minutesAgo}s`
    return `${Math.floor(minutesAgo / 60)}m`
  })

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>
      <div className="relative">
        <svg
          width="100%"
          height="160"
          viewBox={`0 0 ${chartWidth + marginLeft + 20} ${chartHeight + marginBottom + 20}`}
          className="w-full"
        >
          {/* Grid lines */}
          <defs>
            <pattern id={`grid-${color}`} width="40" height="20" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 20" fill="none" stroke="#f3f4f6" strokeWidth="0.5"/>
            </pattern>
          </defs>
          <rect x={marginLeft} y="0" width={chartWidth} height={chartHeight} fill={`url(#grid-${color})`} />
          
          {/* Y-axis */}
          <line x1={marginLeft} y1="0" x2={marginLeft} y2={chartHeight} stroke="#d1d5db" strokeWidth="1"/>
          
          {/* X-axis */}
          <line x1={marginLeft} y1={chartHeight} x2={marginLeft + chartWidth} y2={chartHeight} stroke="#d1d5db" strokeWidth="1"/>
          
          {/* Y-axis labels */}
          <text x={marginLeft - 5} y="5" textAnchor="end" className="text-xs fill-gray-500" fontSize="10">
            {Math.round(maxValue)}{unit}
          </text>
          <text x={marginLeft - 5} y={chartHeight / 2} textAnchor="end" className="text-xs fill-gray-500" fontSize="10">
            {Math.round((maxValue + minValue) / 2)}{unit}
          </text>
          <text x={marginLeft - 5} y={chartHeight + 5} textAnchor="end" className="text-xs fill-gray-500" fontSize="10">
            {Math.round(minValue)}{unit}
          </text>
          
          {/* Chart line */}
          <polyline
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            points={points}
            className={colorClasses[color]}
          />
          
          {/* Data points */}
          {data.map((value, index) => {
            const x = marginLeft + (index / (data.length - 1)) * chartWidth
            const y = chartHeight - ((value - minValue) / (maxValue - minValue)) * chartHeight
            return (
              <circle
                key={index}
                cx={x}
                cy={y}
                r="3"
                fill="currentColor"
                className={colorClasses[color]}
              />
            )
          })}
          
          {/* X-axis labels (time) - rotated to avoid overlap */}
          {timeLabels.map((label, index) => {
            // Only show first, middle, and last labels
            if (index === 0 || index === Math.floor(timeLabels.length / 2) || index === timeLabels.length - 1) {
              const x = marginLeft + (index / (data.length - 1)) * chartWidth
              return (
                <text 
                  key={index}
                  x={x} 
                  y={chartHeight + 20} 
                  textAnchor="middle" 
                  className="text-xs fill-gray-500" 
                  fontSize="9"
                  transform={`rotate(-45 ${x} ${chartHeight + 20})`}
                >
                  {label}
                </text>
              )
            }
            return null
          })}
        </svg>
        
        {/* Y-axis title */}
        <div className="absolute left-2 top-1/2 transform -rotate-90 -translate-y-1/2 text-xs text-gray-500 font-medium">
          Usage ({unit})
        </div>
        
        {/* X-axis title */}
        <div className="text-center mt-2 text-xs text-gray-500 font-medium">
          Time (ago)
        </div>
      </div>
    </div>
  )
}

export default SystemChart
