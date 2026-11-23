import { useState } from "react";
import {
    Activity,
    BrainCircuit,
    TrendingUp,
    AlertTriangle,
    Sparkles,
    Loader2,
    RefreshCw
} from "lucide-react";

import {
    ResponsiveContainer,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend
} from "recharts";

import { generatePredictiveInsights } from "../services/api";
import ReactMarkdown from "react-markdown";

// Convert a forecast metric into chart-friendly data.
// Supports common month/date and value field names.
const getChartData = (metric) => {
    if (!metric) return [];

    const history = (metric.history || []).map((item) => ({
        month: item.month || item.date || item.period,
        actual: Number(
            item.value ?? item.actual ?? item.revenue ?? item.profit
        ),
        predicted: null
    }));

    const forecast = (metric.forecast || []).map((item) => ({
        month: item.month || item.date || item.period,
        actual: null,
        predicted: Number(
            item.value ??
            item.predicted ??
            item.forecast ??
            item.revenue ??
            item.profit
        )
    }));

    // Connect the forecast line to the last historical value.
    if (history.length > 0 && forecast.length > 0) {
        const lastHistorical = history[history.length - 1];

        if (Number.isFinite(lastHistorical.actual)) {
            lastHistorical.predicted = lastHistorical.actual;
        }
    }

    return [...history, ...forecast].filter(
        (item) =>
            item.month &&
            (
                Number.isFinite(item.actual) ||
                Number.isFinite(item.predicted)
            )
    );
};

const formatValue = (value) =>
    Number(value).toLocaleString(undefined, {
        maximumFractionDigits: 2
    });

function ForecastChart({ title, metric }) {
    const chartData = getChartData(metric);

    if (!metric || metric.status !== "completed" || !chartData.length) {
        return (
            <div className="bg-white rounded-xl border border-slate-200 p-6">
                <h3 className="font-semibold text-slate-800">{title}</h3>
                <p className="text-sm text-slate-500 mt-3">
                    Forecast data is not available for this metric.
                </p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
            <div className="mb-5">
                <h3 className="font-semibold text-slate-900">{title}</h3>
                <p className="text-sm text-slate-500 mt-1">
                    Historical performance and projected values
                </p>
            </div>

            <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />

                        <XAxis
                            dataKey="month"
                            tick={{ fontSize: 12 }}
                            tickLine={false}
                        />

                        <YAxis
                            tickFormatter={formatValue}
                            tick={{ fontSize: 12 }}
                            tickLine={false}
                        />

                        <Tooltip
                            formatter={(value) => formatValue(value)}
                        />

                        <Legend />

                        <Line
                            type="monotone"
                            dataKey="actual"
                            name="Historical"
                            stroke="#2563eb"
                            strokeWidth={2.5}
                            connectNulls={false}
                            dot={{ r: 4 }}
                        />

                        <Line
                            type="monotone"
                            dataKey="predicted"
                            name="Forecast"
                            stroke="#16a34a"
                            strokeWidth={2.5}
                            strokeDasharray="6 4"
                            connectNulls={false}
                            dot={{ r: 4 }}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}

function PredictiveDashboard({ forecast, file }) {
    const [insights, setInsights] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const metrics = forecast?.metrics || {};

    const revenue = metrics.revenue;
    const profit = metrics.profit;

    const forecastAvailable =
        revenue?.status === "completed" ||
        profit?.status === "completed";

    const handleGenerateInsights = async () => {
        if (!file) return;

        try {
            setLoading(true);
            setError("");
            setInsights(null);

            const result = await generatePredictiveInsights(file);

            if (result.status !== "completed" || !result.insights) {
                setError(
                    "AI insights could not be generated. The dataset may not contain enough historical data."
                );
                return;
            }

            setInsights(result.insights);
        } catch (err) {
            console.error("Predictive insights error:", err);

            setError(
                err.response?.data?.detail ||
                "Unable to generate predictive insights. Please try again."
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <section className="space-y-6">

            {/* Section Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <div className="flex items-center gap-2">
                        <Activity className="text-blue-600" size={22} />

                        <h2 className="text-xl font-bold text-slate-900">
                            Predictive Analytics
                        </h2>
                    </div>

                    <p className="text-sm text-slate-500 mt-2">
                        Forecast future performance using historical dataset trends.
                    </p>
                </div>

                <button
                    onClick={handleGenerateInsights}
                    disabled={loading || !forecastAvailable || !file}
                    className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {loading ? (
                        <>
                            <Loader2 size={17} className="animate-spin" />
                            Generating Insights...
                        </>
                    ) : insights ? (
                        <>
                            <RefreshCw size={17} />
                            Regenerate AI Insights
                        </>
                    ) : (
                        <>
                            <Sparkles size={17} />
                            Generate AI Insights
                        </>
                    )}
                </button>
            </div>

            {/* Forecast Status */}
            {!forecastAvailable && (
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-5">
                    <div className="flex gap-3">
                        <AlertTriangle className="text-amber-600 shrink-0" />

                        <div>
                            <h3 className="font-semibold text-amber-900">
                                Forecast unavailable
                            </h3>

                            <p className="text-sm text-amber-800 mt-1">
                                {forecast?.message ||
                                    "This dataset does not have enough historical data to generate a forecast."}
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* Forecast Charts */}
            {forecastAvailable && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <ForecastChart
                        title="Revenue Forecast"
                        metric={revenue}
                    />

                    <ForecastChart
                        title="Profit Forecast"
                        metric={profit}
                    />
                </div>
            )}

            {/* Forecast Information */}
            {forecastAvailable && (
                <div className="bg-blue-50 border border-blue-100 rounded-xl p-5">
                    <div className="flex gap-3">
                        <TrendingUp className="text-blue-600 shrink-0" />

                        <div>
                            <h3 className="font-semibold text-slate-900">
                                Forecast Methodology
                            </h3>

                            <p className="text-sm text-slate-600 mt-1">
                                InsightIQ uses Holt's damped trend exponential smoothing
                                to estimate future values from historical monthly data.
                                Forecasts are estimates, not guaranteed outcomes.
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* AI Insights */}
            {error && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-5">
                    <p className="text-sm text-red-700">{error}</p>
                </div>
            )}

            {insights && (
                <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                    <div className="flex items-center gap-3 mb-5">
                        <div className="bg-purple-100 text-purple-700 p-2 rounded-lg">
                            <BrainCircuit size={22} />
                        </div>

                        <div>
                            <h3 className="font-semibold text-slate-900">
                                AI Predictive Insights
                            </h3>

                            <p className="text-xs text-slate-500">
                                Generated by Gemini based on your dataset and forecast
                            </p>
                        </div>
                    </div>

                    <div className="text-sm leading-7 text-slate-700">
                        <ReactMarkdown
                            components={{
                                h1: ({ children }) => (
                                    <h1 className="text-xl font-bold text-slate-900 mt-6 mb-3">
                                        {children}
                                    </h1>
                                ),
                                h2: ({ children }) => (
                                    <h2 className="text-lg font-semibold text-slate-900 mt-6 mb-3">
                                        {children}
                                    </h2>
                                ),
                                h3: ({ children }) => (
                                    <h3 className="text-base font-semibold text-slate-800 mt-4 mb-2">
                                        {children}
                                    </h3>
                                ),
                                p: ({ children }) => (
                                    <p className="mb-4">
                                        {children}
                                    </p>
                                ),
                                ul: ({ children }) => (
                                    <ul className="list-disc pl-6 mb-4 space-y-2">
                                        {children}
                                    </ul>
                                ),
                                ol: ({ children }) => (
                                    <ol className="list-decimal pl-6 mb-4 space-y-2">
                                        {children}
                                    </ol>
                                ),
                                li: ({ children }) => (
                                    <li>{children}</li>
                                ),
                                strong: ({ children }) => (
                                    <strong className="font-semibold text-slate-900">
                                        {children}
                                    </strong>
                                ),
                                hr: () => (
                                    <hr className="my-5 border-slate-200" />
                                )
                            }}
                        >
                            {insights}
                        </ReactMarkdown>
                    </div>
                </div>
            )}

        </section>
    );
}

export default PredictiveDashboard;
