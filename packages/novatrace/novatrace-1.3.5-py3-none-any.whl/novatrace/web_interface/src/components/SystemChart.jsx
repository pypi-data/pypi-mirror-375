import React from 'react'

const SystemChart = ({ title, data, labels, color = 'blue', unit = '%' }) => {
  const colorClasses = {
    blue: 'stroke-blue-500',
    green: 'stroke-green-500',
    purple: 'stroke-purple-500',
    orange: 'stroke-orange-500',
  }

  // Handle empty data
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>
        <div className="flex items-center justify-center h-32 text-gray-500">
          No historical data available
        </div>
      </div>
    )
  }

  // Simple line chart using SVG with proper margins for axes
  // Always use 0-100% scale for visual consistency and real usage perspective
  const maxValue = 100  // Fixed at 100%
  const minValue = 0    // Fixed at 0%
  const chartWidth = 280
  const chartHeight = 100
  const marginLeft = 40
  const marginBottom = 20
  const marginTop = 15  // Add top margin to prevent cutting
  
  const points = data.map((value, index) => {
    const x = marginLeft + (index / Math.max(data.length - 1, 1)) * chartWidth
    const y = marginTop + chartHeight - ((value - minValue) / (maxValue - minValue)) * chartHeight
    return `${x},${y}`
  }).join(' ')

  // Use provided labels or generate compact time labels in h:m format
  const timeLabels = labels ? labels.map(label => {
    // If label is already a time string, try to format it to h:m
    if (typeof label === 'string' && label.includes(':')) {
      // Extract time from various formats like "11:03:06 PM" or "2023-09-08 11:03:06"
      const timeMatch = label.match(/(\d{1,2}):(\d{2})/)
      if (timeMatch) {
        return `${timeMatch[1]}:${timeMatch[2]}`
      }
      return label
    }
    return label
  }) : data.map((_, index) => {
    const minutesAgo = (data.length - 1 - index) * 15 // 15 minute intervals
    if (minutesAgo === 0) {
      const now = new Date()
      return `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`
    }
    const timeAgo = new Date(Date.now() - minutesAgo * 60000)
    return `${timeAgo.getHours()}:${timeAgo.getMinutes().toString().padStart(2, '0')}`
  })

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-4">
      <h3 className="text-lg font-medium text-gray-900 ">{title}</h3>
      <div className="relative">
        <svg
          width="100%"
          height="140%"
          viewBox={`0 0 ${chartWidth + marginLeft + 20} ${chartHeight + marginBottom + marginTop + 10}`}
          className="w-full mt-2"
        >
          {/* Grid lines */}
          <defs>
            <pattern id={`grid-${color}`} width="40" height="20" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 20" fill="none" stroke="#f3f4f6" strokeWidth="0.5"/>
            </pattern>
          </defs>
          <rect x={marginLeft} y={marginTop} width={chartWidth} height={chartHeight} fill={`url(#grid-${color})`} />
          
          {/* Y-axis */}
          <line x1={marginLeft} y1={marginTop} x2={marginLeft} y2={marginTop + chartHeight} stroke="#d1d5db" strokeWidth="1"/>
          
          {/* X-axis */}
          <line x1={marginLeft} y1={marginTop + chartHeight} x2={marginLeft + chartWidth} y2={marginTop + chartHeight} stroke="#d1d5db" strokeWidth="1"/>
          
          {/* Y-axis labels */}
          <text x={marginLeft - 5} y={marginTop + 5} textAnchor="end" className="text-xs fill-gray-500" fontSize="10">
            100{unit}
          </text>
          <text x={marginLeft - 5} y={marginTop + chartHeight / 2} textAnchor="end" className="text-xs fill-gray-500" fontSize="10">
            50{unit}
          </text>
          <text x={marginLeft - 5} y={marginTop + chartHeight + 5} textAnchor="end" className="text-xs fill-gray-500" fontSize="10">
            0{unit}
          </text>
          
          {/* Chart line */}
          <polyline
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            points={points}
            className={colorClasses[color]}
          />
          
          {/* X-axis labels (time) - show only 3 labels to avoid overlap */}
          {timeLabels.map((label, index) => {
            // Only show first, middle, and last labels
            const showLabel = index === 0 || 
                             index === Math.floor(timeLabels.length / 2) || 
                             index === timeLabels.length - 1
            
            if (showLabel) {
              const x = marginLeft + (index / Math.max(data.length - 1, 1)) * chartWidth
              return (
                <text 
                  key={index}
                  x={x} 
                  y={marginTop + chartHeight + 20} 
                  textAnchor="middle" 
                  className="text-xs fill-gray-500" 
                  fontSize="8"
                >
                  {label}
                </text>
              )
            }
            return null
          })}
        </svg>
        
        {/* Y-axis title */}
        <div className="absolute -left-6 top-1/2 transform -rotate-90 -translate-y-1/2 text-xs text-gray-500 font-medium">
          Usage ({unit})
        </div>
        
        {/* X-axis title */}
        <div className="text-center mt-0 text-xs text-gray-500 font-medium">
          Time
        </div>
      </div>
    </div>
  )
}

export default SystemChart
