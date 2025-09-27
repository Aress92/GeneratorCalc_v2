import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowUpIcon, ArrowDownIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  change?: number;
  changeType?: 'increase' | 'decrease';
  icon?: React.ReactNode;
  color?: 'blue' | 'green' | 'orange' | 'red' | 'purple';
  loading?: boolean;
}

const colorClasses = {
  blue: {
    icon: 'text-blue-600',
    background: 'bg-blue-50',
    border: 'border-blue-200'
  },
  green: {
    icon: 'text-green-600',
    background: 'bg-green-50',
    border: 'border-green-200'
  },
  orange: {
    icon: 'text-orange-600',
    background: 'bg-orange-50',
    border: 'border-orange-200'
  },
  red: {
    icon: 'text-red-600',
    background: 'bg-red-50',
    border: 'border-red-200'
  },
  purple: {
    icon: 'text-purple-600',
    background: 'bg-purple-50',
    border: 'border-purple-200'
  }
};

export default function MetricCard({
  title,
  value,
  unit,
  change,
  changeType,
  icon,
  color = 'blue',
  loading = false
}: MetricCardProps) {
  const colorClass = colorClasses[color];

  if (loading) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-gray-500">
            <div className="animate-pulse bg-gray-300 rounded h-4 w-24"></div>
          </CardTitle>
          <div className={`p-2 rounded-md ${colorClass.background}`}>
            <div className="animate-pulse bg-gray-300 rounded h-5 w-5"></div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse bg-gray-300 rounded h-8 w-16 mb-2"></div>
          <div className="animate-pulse bg-gray-300 rounded h-4 w-12"></div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`${colorClass.border} border transition-all hover:shadow-lg`}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-gray-600">
          {title}
        </CardTitle>
        {icon && (
          <div className={`p-2 rounded-md ${colorClass.background}`}>
            <div className={`h-5 w-5 ${colorClass.icon}`}>
              {icon}
            </div>
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline space-x-1">
          <div className="text-2xl font-bold text-gray-900">
            {typeof value === 'number' ? value.toLocaleString() : value}
          </div>
          {unit && (
            <div className="text-sm text-gray-500 font-medium">
              {unit}
            </div>
          )}
        </div>

        {change !== undefined && (
          <div className="mt-2 flex items-center space-x-1">
            {changeType === 'increase' ? (
              <ArrowUpIcon className="h-4 w-4 text-green-600" />
            ) : (
              <ArrowDownIcon className="h-4 w-4 text-red-600" />
            )}
            <span className={`text-sm font-medium ${
              changeType === 'increase' ? 'text-green-600' : 'text-red-600'
            }`}>
              {Math.abs(change)}% vs last month
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}