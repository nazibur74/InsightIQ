import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  BarChart,
  Bar
} from "recharts";

import {
  TrendingUp,
  DollarSign,
  Database,
  Percent,
  BarChart3
} from "lucide-react";


function formatValue(value, format) {
  if (value === null || value === undefined) return "N/A";

  if (format === "currency") {
    return Number(value).toLocaleString(undefined, {
      maximumFractionDigits: 2
    });
  }

  if (format === "percentage") {
    return `${Number(value).toFixed(2)}%`;
  }

  return Number(value).toLocaleString();
}


function getKpiIcon(label) {
  const name = label.toLowerCase();

  if (name.includes("profit") && name.includes("margin")) {
    return Percent;
  }

  if (name.includes("revenue") || name.includes("profit")) {
    return DollarSign;
  }

  if (name.includes("record") || name.includes("column")) {
    return Database;
  }

  return BarChart3;
}


function AnalyticsDashboard({ analytics }) {
  if (!analytics) return null;

  const {
    kpis = [],
    monthly_trend = [],
    category_comparison = [],
    category_column,
    category_metric,
    numeric_summaries = []
  } = analytics;

  return (
    <section className="mt-10 space-y-8">

      {/* Dashboard Heading */}
      <div>
        <div className="flex items-center gap-2">
          <TrendingUp className="text-indigo-600" size={25} />

          <h2 className="text-2xl font-bold text-gray-900">
            Analytics Dashboard
          </h2>
        </div>

        <p className="mt-1 text-sm text-gray-500">
          Explore key performance indicators and business trends
          generated from your dataset.
        </p>
      </div>


      {/* KPI Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">

        {kpis.map((kpi, index) => {
          const Icon = getKpiIcon(kpi.label);

          return (
            <div
              key={`${kpi.label}-${index}`}
              className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
            >
              <div className="flex items-center justify-between">

                <p className="text-sm font-medium text-gray-500">
                  {kpi.label}
                </p>

                <div className="rounded-lg bg-indigo-50 p-2">
                  <Icon size={19} className="text-indigo-600" />
                </div>

              </div>

              <h3 className="mt-4 break-words text-2xl font-bold text-gray-900">
                {formatValue(kpi.value, kpi.format)}
              </h3>

              {kpi.column && (
                <p className="mt-1 text-xs text-gray-400">
                  Based on {kpi.column}
                </p>
              )}
            </div>
          );
        })}

      </div>


      {/* Monthly Trend Chart */}
      <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">

        <div className="mb-6">
          <h3 className="font-semibold text-gray-900">
            Revenue & Profit Trend
          </h3>

          <p className="mt-1 text-sm text-gray-500">
            Monthly performance over time
          </p>
        </div>

        {monthly_trend.length > 0 ? (
          <div className="h-80 w-full">

            <ResponsiveContainer width="100%" height="100%">

              <LineChart
                data={monthly_trend}
                margin={{
                  top: 10,
                  right: 20,
                  left: 10,
                  bottom: 5
                }}
              >

                <CartesianGrid strokeDasharray="3 3" />

                <XAxis
                  dataKey="month"
                  tick={{ fontSize: 12 }}
                />

                <YAxis
                  tick={{ fontSize: 12 }}
                />

                <Tooltip
                  formatter={(value) =>
                    Number(value).toLocaleString()
                  }
                />

                <Legend />

                {monthly_trend.some(item =>
                  item.revenue !== undefined
                ) && (
                  <Line
                    type="monotone"
                    dataKey="revenue"
                    name="Revenue"
                    stroke="#4F46E5"
                    strokeWidth={3}
                    activeDot={{ r: 6 }}
                  />
                )}

                {monthly_trend.some(item =>
                  item.profit !== undefined
                ) && (
                  <Line
                    type="monotone"
                    dataKey="profit"
                    name="Profit"
                    stroke="#16A34A"
                    strokeWidth={3}
                    activeDot={{ r: 6 }}
                  />
                )}

              </LineChart>

            </ResponsiveContainer>

          </div>
        ) : (
          <div className="rounded-lg bg-gray-50 p-10 text-center">
            <p className="font-medium text-gray-700">
              No time-series data available
            </p>

            <p className="mt-2 text-sm text-gray-500">
              A valid date column and numeric business metric
              are required to generate this chart.
            </p>
          </div>
        )}

      </div>


      {/* Category Comparison */}
      <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">

        <div className="mb-6">
          <h3 className="font-semibold text-gray-900">
            Category Performance
          </h3>

          <p className="mt-1 text-sm text-gray-500">
            {category_column
              ? `Comparison by ${category_column}`
              : "Comparison across available categories"}
          </p>
        </div>

        {category_comparison.length > 0 ? (
          <div className="h-80 w-full">

            <ResponsiveContainer width="100%" height="100%">

              <BarChart
                data={category_comparison}
                margin={{
                  top: 10,
                  right: 20,
                  left: 10,
                  bottom: 35
                }}
              >

                <CartesianGrid strokeDasharray="3 3" />

                <XAxis
                  dataKey="category"
                  angle={-15}
                  textAnchor="end"
                  interval={0}
                  tick={{ fontSize: 12 }}
                />

                <YAxis
                  tick={{ fontSize: 12 }}
                />

                <Tooltip
                  formatter={(value) =>
                    Number(value).toLocaleString()
                  }
                />

                <Bar
                  dataKey="value"
                  name={category_metric || "Value"}
                  fill="#6366F1"
                  radius={[6, 6, 0, 0]}
                />

              </BarChart>

            </ResponsiveContainer>

          </div>
        ) : (
          <div className="rounded-lg bg-gray-50 p-10 text-center">
            <p className="font-medium text-gray-700">
              No category comparison available
            </p>

            <p className="mt-2 text-sm text-gray-500">
              At least two distinct category values and a numeric
              metric are needed.
            </p>
          </div>
        )}

      </div>


      {/* Numeric Summary Table */}
      <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">

        <div className="border-b border-gray-100 p-5">
          <h3 className="font-semibold text-gray-900">
            Numeric Data Summary
          </h3>

          <p className="mt-1 text-sm text-gray-500">
            Statistical overview of numeric columns
          </p>
        </div>

        {numeric_summaries.length > 0 ? (
          <div className="overflow-x-auto">

            <table className="w-full text-left text-sm">

              <thead className="bg-gray-50 text-gray-600">
                <tr>
                  <th className="px-5 py-3">Column</th>
                  <th className="px-5 py-3">Mean</th>
                  <th className="px-5 py-3">Median</th>
                  <th className="px-5 py-3">Minimum</th>
                  <th className="px-5 py-3">Maximum</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-gray-100">

                {numeric_summaries.map((item, index) => (
                  <tr key={`${item.column}-${index}`}>

                    <td className="px-5 py-4 font-medium text-gray-900">
                      {item.column}
                    </td>

                    <td className="px-5 py-4">
                      {formatValue(item.mean, "number")}
                    </td>

                    <td className="px-5 py-4">
                      {formatValue(item.median, "number")}
                    </td>

                    <td className="px-5 py-4">
                      {formatValue(item.min, "number")}
                    </td>

                    <td className="px-5 py-4">
                      {formatValue(item.max, "number")}
                    </td>

                  </tr>
                ))}

              </tbody>

            </table>

          </div>
        ) : (
          <p className="p-5 text-sm text-gray-500">
            No numeric columns available.
          </p>
        )}

      </div>

    </section>
  );
}

export default AnalyticsDashboard;
