import React from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'

const MetricCard = ({ title, value, unit, trend, trendValue, icon: Icon, color = 'blue' }) => {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    purple: 'from-purple-500 to-purple-600',
    orange: 'from-orange-500 to-orange-600',
    red: 'from-red-500 to-red-600',
  }

  return (
    <div className={`bg-gradient-to-r ${colorClasses[color]} text-white rounded-lg p-6 shadow-lg`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-blue-100 text-sm font-medium">{title}</p>
          <p className="text-3xl font-bold">
            {value}
            <span className="text-lg font-normal ml-1">{unit}</span>
          </p>
          {trend && (
            <div className="flex items-center mt-2">
              {trend === 'up' ? (
                <TrendingUp className="w-4 h-4 mr-1" />
              ) : (
                <TrendingDown className="w-4 h-4 mr-1" />
              )}
              <span className="text-sm">{trendValue}</span>
            </div>
          )}
        </div>
        {Icon && (
          <div className="bg-white bg-opacity-20 rounded-lg p-3">
            <Icon className="w-8 h-8" />
          </div>
        )}
      </div>
    </div>
  )
}

export default MetricCard
