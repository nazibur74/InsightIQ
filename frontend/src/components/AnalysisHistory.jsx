
import { useEffect, useState } from "react";
import {
    Database,
    FileSpreadsheet,
    CalendarDays,
    Eye,
    Trash2,
    ChevronLeft,
    ChevronRight,
    Loader2,
    RefreshCw,
    AlertCircle,
    Clock
} from "lucide-react";

import {
    getAnalysisHistory,
    getSavedAnalysis,
    deleteDatasetHistory
} from "../services/api";

const PAGE_SIZE = 10;

function formatFileSize(bytes) {
    if (!bytes) return "0 B";

    const units = ["B", "KB", "MB", "GB"];
    const index = Math.min(
        Math.floor(Math.log(bytes) / Math.log(1024)),
        units.length - 1
    );

    return `${(bytes / Math.pow(1024, index)).toFixed(2)} ${units[index]}`;
}

function formatDate(date) {
    if (!date) return "N/A";

    return new Date(date).toLocaleString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit"
    });
}

function AnalysisHistory({ onViewAnalysis }) {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [actionId, setActionId] = useState(null);
    const [skip, setSkip] = useState(0);
    const [hasNextPage, setHasNextPage] = useState(false);

    const loadHistory = async (currentSkip = skip) => {
        try {
            setLoading(true);
            setError("");

            const result = await getAnalysisHistory(
                currentSkip,
                PAGE_SIZE
            );

            setHistory(result.history || []);
            setHasNextPage(
                (result.history || []).length === PAGE_SIZE
            );
        } catch (err) {
            console.error("History loading error:", err);

            setError(
                err.response?.data?.detail ||
                "Unable to load analysis history."
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadHistory(skip);
    }, [skip]);

    const handleView = async (datasetId) => {
        try {
            setActionId(datasetId);
            setError("");

            const result = await getSavedAnalysis(datasetId);

            onViewAnalysis(result);
        } catch (err) {
            console.error("Saved analysis error:", err);

            setError(
                err.response?.data?.detail ||
                "Unable to open saved analysis."
            );
        } finally {
            setActionId(null);
        }
    };

    const handleDelete = async (dataset) => {
        const confirmed = window.confirm(
            `Are you sure you want to delete "${dataset.filename}"?\n\nThis will permanently remove its saved analysis and uploaded file.`
        );

        if (!confirmed) return;

        try {
            setActionId(dataset.dataset_id);
            setError("");

            await deleteDatasetHistory(dataset.dataset_id);

            // Reload the current page after deletion.
            if (history.length === 1 && skip > 0) {
                setSkip(Math.max(0, skip - PAGE_SIZE));
            } else {
                await loadHistory(skip);
            }
        } catch (err) {
            console.error("History deletion error:", err);

            setError(
                err.response?.data?.detail ||
                "Unable to delete this dataset."
            );
        } finally {
            setActionId(null);
        }
    };

    return (
        <div className="space-y-6">

            {/* Page Header */}
            <div className="flex flex-wrap justify-between items-center gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-slate-900">
                        Analysis History
                    </h2>

                    <p className="text-sm text-slate-500 mt-1">
                        Access and manage your previously analyzed datasets.
                    </p>
                </div>

                <button
                    onClick={() => loadHistory(skip)}
                    disabled={loading}
                    className="inline-flex items-center gap-2 px-4 py-2.5 border border-slate-300 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
                >
                    <RefreshCw
                        size={16}
                        className={loading ? "animate-spin" : ""}
                    />
                    Refresh
                </button>
            </div>

            {/* Error Message */}
            {error && (
                <div className="flex items-center gap-3 p-4 rounded-lg border border-red-200 bg-red-50 text-red-700">
                    <AlertCircle size={19} />
                    <p className="text-sm">{error}</p>
                </div>
            )}

            {/* History Table */}
            <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">

                {loading ? (
                    <div className="py-20 flex flex-col items-center">
                        <Loader2
                            size={32}
                            className="animate-spin text-blue-600"
                        />
                        <p className="text-sm text-slate-500 mt-4">
                            Loading your analysis history...
                        </p>
                    </div>
                ) : history.length === 0 ? (
                    <div className="py-20 text-center">
                        <Database
                            size={42}
                            className="mx-auto text-slate-300"
                        />

                        <h3 className="font-semibold text-slate-800 mt-4">
                            No analysis history found
                        </h3>

                        <p className="text-sm text-slate-500 mt-2">
                            Upload a dataset to start building your history.
                        </p>
                    </div>
                ) : (
                    <>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left text-sm">

                                <thead className="bg-slate-50 text-slate-500">
                                    <tr>
                                        <th className="px-6 py-4 font-medium">
                                            Dataset
                                        </th>
                                        <th className="px-6 py-4 font-medium">
                                            Records
                                        </th>
                                        <th className="px-6 py-4 font-medium">
                                            File Size
                                        </th>
                                        <th className="px-6 py-4 font-medium">
                                            Uploaded
                                        </th>
                                        <th className="px-6 py-4 font-medium">
                                            Analyses
                                        </th>
                                        <th className="px-6 py-4 font-medium text-right">
                                            Actions
                                        </th>
                                    </tr>
                                </thead>

                                <tbody>
                                    {history.map((dataset) => (
                                        <tr
                                            key={dataset.dataset_id}
                                            className="border-t border-slate-100 hover:bg-slate-50 transition-colors"
                                        >
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-3">
                                                    <div className="p-2 bg-blue-50 rounded-lg">
                                                        <FileSpreadsheet
                                                            size={20}
                                                            className="text-blue-600"
                                                        />
                                                    </div>

                                                    <div>
                                                        <p className="font-medium text-slate-800">
                                                            {dataset.filename}
                                                        </p>

                                                        <p className="text-xs text-slate-400 uppercase mt-1">
                                                            {dataset.file_type}
                                                        </p>
                                                    </div>
                                                </div>
                                            </td>

                                            <td className="px-6 py-4 text-slate-600">
                                                {dataset.row_count?.toLocaleString() ?? "N/A"}
                                            </td>

                                            <td className="px-6 py-4 text-slate-600">
                                                {formatFileSize(dataset.file_size)}
                                            </td>

                                            <td className="px-6 py-4 text-slate-600">
                                                <div className="flex items-center gap-2">
                                                    <CalendarDays
                                                        size={15}
                                                        className="text-slate-400"
                                                    />
                                                    {formatDate(dataset.uploaded_at)}
                                                </div>
                                            </td>

                                            <td className="px-6 py-4">
                                                <span className="px-2.5 py-1 rounded-full bg-green-50 text-green-700 text-xs font-medium">
                                                    {dataset.analysis_count}
                                                </span>
                                            </td>

                                            <td className="px-6 py-4">
                                                <div className="flex justify-end items-center gap-2">

                                                    <button
                                                        onClick={() => handleView(dataset.dataset_id)}
                                                        disabled={actionId === dataset.dataset_id}
                                                        title="View analysis"
                                                        className="p-2 rounded-lg text-blue-600 hover:bg-blue-50 disabled:opacity-50"
                                                    >
                                                        {actionId === dataset.dataset_id ? (
                                                            <Loader2 size={18} className="animate-spin" />
                                                        ) : (
                                                            <Eye size={18} />
                                                        )}
                                                    </button>

                                                    <button
                                                        onClick={() => handleDelete(dataset)}
                                                        disabled={actionId === dataset.dataset_id}
                                                        title="Delete dataset"
                                                        className="p-2 rounded-lg text-red-500 hover:bg-red-50 disabled:opacity-50"
                                                    >
                                                        <Trash2 size={18} />
                                                    </button>

                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>

                            </table>
                        </div>

                        {/* Pagination */}
                        <div className="flex flex-wrap justify-between items-center gap-3 px-6 py-4 border-t border-slate-100">

                            <p className="text-sm text-slate-500">
                                Showing {skip + 1}–{skip + history.length} datasets
                            </p>

                            <div className="flex items-center gap-2">
                                <button
                                    onClick={() => setSkip(Math.max(0, skip - PAGE_SIZE))}
                                    disabled={skip === 0 || loading}
                                    className="inline-flex items-center gap-1 px-3 py-2 rounded-lg border border-slate-300 text-sm text-slate-600 hover:bg-slate-50 disabled:opacity-40"
                                >
                                    <ChevronLeft size={16} />
                                    Previous
                                </button>

                                <button
                                    onClick={() => setSkip(skip + PAGE_SIZE)}
                                    disabled={!hasNextPage || loading}
                                    className="inline-flex items-center gap-1 px-3 py-2 rounded-lg border border-slate-300 text-sm text-slate-600 hover:bg-slate-50 disabled:opacity-40"
                                >
                                    Next
                                    <ChevronRight size={16} />
                                </button>
                            </div>

                        </div>
                    </>
                )}
            </div>

            <div className="flex items-center gap-2 text-xs text-slate-400">
                <Clock size={14} />
                Your history is stored in your InsightIQ PostgreSQL database.
            </div>

        </div>
    );
}

export default AnalysisHistory;
