import { useState } from "react";

import FileUploader from "./components/FileUploader";
import QualityReport from "./components/QualityReport";
import BusinessDiagnostics from "./components/BusinessDiagnostics";
import AnalyticsDashboard from "./components/AnalyticsDashboard";
import PredictiveDashboard from "./components/PredictiveDashboard";
import AIChat from "./components/AIChat";
import AnalysisHistory from "./components/AnalysisHistory";
import Sidebar, { NAV_ITEMS } from "./components/Sidebar";
import Footer from "./components/Footer";

import { filterDatasetAnalytics, generatePdfReport } from "./services/api";

import {
  Database,
  FileSpreadsheet,
  Activity,
  AlertTriangle,
  Filter,
  RotateCcw,
  Loader2,
  FileDown,
  Menu,
  ArrowRight
} from "lucide-react";


function App() {
  const [analysis, setAnalysis] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  const [analytics, setAnalytics] = useState(null);

  const [filters, setFilters] = useState({
    startDate: "",
    endDate: "",
    category: "All"
  });

  const [loading, setLoading] = useState(false);
  const [filterError, setFilterError] = useState("");
  const [reportLoading, setReportLoading] = useState(false);
  const [reportError, setReportError] = useState("");
  const [activeView, setActiveView] = useState("overview");
  const [isSavedAnalysis, setIsSavedAnalysis] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const overview = analysis?.profile?.overview;

  // ----------------------------------------
  // Handle initial upload
  // ----------------------------------------

  const handleUploadSuccess = (result, file) => {
    setAnalysis(result);
    setSelectedFile(file);
    setIsSavedAnalysis(false);
    setActiveView("overview");

    setAnalytics(result.analytics);

    setFilters({
      startDate: "",
      endDate: "",
      category: "All"
    });

    setFilterError("");
    setReportError("");
  };


  // ----------------------------------------
  // Restore a saved analysis from PostgreSQL
  // ----------------------------------------

  const handleViewSavedAnalysis = (result) => {
    const restoredAnalysis = {
      ...result.analysis,
      filename: result.dataset.filename,
      dataset_id: result.dataset.id
    };

    setAnalysis(restoredAnalysis);
    setSelectedFile(null);
    setAnalytics(restoredAnalysis.analytics || null);
    setIsSavedAnalysis(true);
    setActiveView("overview");

    setFilters({
      startDate: "",
      endDate: "",
      category: "All"
    });

    setFilterError("");
  };

  // ----------------------------------------
  // Generate and download PDF report
  // ----------------------------------------

  const handleDownloadReport = async () => {
    if (!selectedFile) {
      setReportError("The original dataset is not available. Upload the file again to generate a report.");
      return;
    }

    try {
      setReportLoading(true);
      setReportError("");

      const response = await generatePdfReport(selectedFile);
      const pdfBlob = new Blob([response.data], {
        type: "application/pdf"
      });

      const downloadUrl = window.URL.createObjectURL(pdfBlob);
      const link = document.createElement("a");
      const originalName = selectedFile.name.replace(/\.[^/.]+$/, "");
      const disposition = response.headers["content-disposition"];
      const filenameMatch = disposition?.match(/filename="?([^"]+)"?/i);
      const filename = filenameMatch?.[1] || `${originalName}_InsightIQ_Report.pdf`;

      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();

      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error("PDF report generation error:", error);
      setReportError(
        "Unable to generate the PDF report. Please try again."
      );
    } finally {
      setReportLoading(false);
    }
  };


  // ----------------------------------------
  // Update filter values
  // ----------------------------------------

  const handleFilterChange = (name, value) => {
    setFilters((previous) => ({
      ...previous,
      [name]: value
    }));
  };


  // ----------------------------------------
  // Apply filters
  // ----------------------------------------

  const handleApplyFilters = async () => {
    if (!selectedFile) {
      setFilterError("Filtering a reopened analysis will be available once saved-dataset filtering is added.");
      return;
    }

    if (
      filters.startDate &&
      filters.endDate &&
      filters.startDate > filters.endDate
    ) {
      setFilterError("Start date cannot be after end date.");
      return;
    }

    try {
      setLoading(true);
      setFilterError("");

      const result = await filterDatasetAnalytics(
        selectedFile,
        filters
      );

      // Extract analytics from the API response
      setAnalytics(result.analytics);

    } catch (error) {
      console.error("Filter error:", error);

      setFilterError(
        error.response?.data?.detail ||
        "Unable to apply filters. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };


  // ----------------------------------------
  // Reset filters
  // ----------------------------------------

  const handleResetFilters = () => {
    setFilters({
      startDate: "",
      endDate: "",
      category: "All"
    });

    setAnalytics(analysis?.analytics || null);
    setFilterError("");
  };


  // ----------------------------------------
  // Upload another dataset
  // ----------------------------------------

  const handleNewUpload = () => {
    setAnalysis(null);
    setSelectedFile(null);
    setAnalytics(null);
    setIsSavedAnalysis(false);
    setActiveView("overview");

    setFilters({
      startDate: "",
      endDate: "",
      category: "All"
    });

    setFilterError("");
    setReportError("");
  };


  const filterOptions = analytics?.filters;

  const hasActiveFilters =
    filters.startDate ||
    filters.endDate ||
    filters.category !== "All";

  const currentNav =
    NAV_ITEMS.find((item) => item.id === activeView) || NAV_ITEMS[0];

  // Keeps sections mounted (so chat history, AI insights and filters are
  // preserved when switching pages) and simply hides inactive ones.
  const show = (id) => (activeView === id ? "" : "hidden");

  const inputClass =
    "w-full rounded-lg border border-slate-300 bg-white p-3 text-sm shadow-sm " +
    "focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-100";


  return (
    <div className="min-h-screen bg-slate-50">

      <Sidebar
        activeView={activeView}
        onNavigate={setActiveView}
        hasAnalysis={Boolean(analysis)}
        filename={analysis?.filename}
        isSavedAnalysis={isSavedAnalysis}
        onNewUpload={handleNewUpload}
        mobileOpen={mobileMenuOpen}
        onClose={() => setMobileMenuOpen(false)}
      />

      <div className="flex min-h-screen flex-col lg:pl-72">

        {/* Top bar */}

        <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/80 backdrop-blur">

          <div className="flex items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-10">

            <div className="flex min-w-0 items-center gap-3">

              <button
                type="button"
                onClick={() => setMobileMenuOpen(true)}
                className="rounded-lg border border-slate-200 p-2 text-slate-600 hover:bg-slate-100 lg:hidden"
                aria-label="Open menu"
              >
                <Menu size={20} />
              </button>

              <div className="min-w-0">
                <h2 className="truncate text-lg font-bold text-slate-900 sm:text-xl">
                  {currentNav.label}
                </h2>

                <p className="hidden truncate text-sm text-slate-500 sm:block">
                  {currentNav.description}
                </p>
              </div>

            </div>

            {analysis && activeView !== "history" && (
              <button
                onClick={handleDownloadReport}
                disabled={!selectedFile || reportLoading}
                title={!selectedFile ? "The original file is required to generate a new report." : "Download PDF report"}
                className="inline-flex shrink-0 items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {reportLoading ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    <span className="hidden sm:inline">Generating PDF...</span>
                  </>
                ) : (
                  <>
                    <FileDown size={16} />
                    <span className="hidden sm:inline">Download PDF Report</span>
                    <span className="sm:hidden">PDF</span>
                  </>
                )}
              </button>
            )}

          </div>

        </header>


        <main className="flex-1 px-4 py-8 sm:px-6 lg:px-10">

          <div className="mx-auto max-w-6xl">

            {/* History */}

            {activeView === "history" && (
              <AnalysisHistory onViewAnalysis={handleViewSavedAnalysis} />
            )}


            {/* Landing: upload */}

            {activeView !== "history" && !analysis && (
              <div className="space-y-8">

                <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-indigo-900 to-blue-800 p-8 text-white shadow-lg sm:p-10">

                  <div className="pointer-events-none absolute -right-16 -top-16 h-64 w-64 rounded-full bg-indigo-500/20 blur-3xl" />

                  <p className="text-xs font-semibold uppercase tracking-widest text-indigo-200">
                    Data Intelligence Platform
                  </p>

                  <h3 className="mt-3 max-w-2xl text-2xl font-bold sm:text-3xl">
                    Discover what your data is telling you.
                  </h3>

                  <p className="mt-3 max-w-2xl text-sm text-indigo-100 sm:text-base">
                    Upload your spreadsheet and let InsightIQ
                    analyze, diagnose and uncover insights.
                  </p>

                </div>

                <FileUploader onSuccess={handleUploadSuccess} />

              </div>
            )}


            {/* Analysis workspace (kept mounted while a dataset is loaded) */}

            {analysis && (
              <div className={`space-y-6 ${activeView === "history" ? "hidden" : ""}`}>

                {/* Dataset status strip */}

                <div className="flex flex-wrap items-center gap-x-4 gap-y-2 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm shadow-sm">

                  <span className="inline-flex items-center gap-2 text-slate-600">
                    <FileSpreadsheet size={16} className="text-indigo-600" />
                    File:{" "}
                    <strong className="break-all font-medium text-slate-900">
                      {analysis.filename}
                    </strong>
                  </span>

                  {isSavedAnalysis && (
                    <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
                      Viewing saved analysis
                    </span>
                  )}

                </div>

                {reportError && (
                  <p className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700" role="alert">
                    {reportError}
                  </p>
                )}


                {/* ---------- Overview ---------- */}

                <div className={`space-y-6 ${show("overview")}`}>

                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">

                    {[
                      {
                        label: "Total Records",
                        value: overview?.total_rows,
                        icon: Database,
                        tone: "bg-indigo-50 text-indigo-600"
                      },
                      {
                        label: "Total Columns",
                        value: overview?.total_columns,
                        icon: FileSpreadsheet,
                        tone: "bg-sky-50 text-sky-600"
                      },
                      {
                        label: "Missing Values",
                        value: overview?.missing_values,
                        icon: AlertTriangle,
                        tone: "bg-amber-50 text-amber-600"
                      },
                      {
                        label: "Duplicate Rows",
                        value: overview?.duplicate_rows,
                        icon: Activity,
                        tone: "bg-rose-50 text-rose-600"
                      }
                    ].map((item) => (

                      <div
                        key={item.label}
                        className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
                      >

                        <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${item.tone}`}>
                          <item.icon size={20} />
                        </div>

                        <p className="mt-4 text-sm text-slate-500">
                          {item.label}
                        </p>

                        <h3 className="mt-1 text-2xl font-bold text-slate-900">
                          {(item.value ?? 0).toLocaleString()}
                        </h3>

                      </div>

                    ))}

                  </div>


                  {/* Jump to tools */}

                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">

                    {NAV_ITEMS.filter((item) =>
                      ["quality", "diagnostics", "analytics", "predictive", "assistant"].includes(item.id)
                    ).map((item) => {
                      const Icon = item.icon;

                      return (
                        <button
                          key={item.id}
                          type="button"
                          onClick={() => setActiveView(item.id)}
                          className="group flex items-start gap-3 rounded-xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:border-indigo-300 hover:shadow-md"
                        >
                          <div className="rounded-lg bg-indigo-50 p-2 text-indigo-600">
                            <Icon size={18} />
                          </div>

                          <div className="flex-1">
                            <p className="text-sm font-semibold text-slate-900">
                              {item.label}
                            </p>
                            <p className="mt-1 text-xs text-slate-500">
                              {item.description}
                            </p>
                          </div>

                          <ArrowRight
                            size={16}
                            className="mt-1 text-slate-300 transition group-hover:translate-x-0.5 group-hover:text-indigo-500"
                          />
                        </button>
                      );
                    })}

                  </div>


                  {/* Column Profiles */}

                  <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">

                    <h3 className="mb-4 font-semibold text-slate-900">
                      Column Profiles
                    </h3>

                    <div className="overflow-x-auto">

                      <table className="w-full text-left text-sm">

                        <thead className="bg-slate-50 text-slate-600">
                          <tr>
                            <th className="p-3 font-medium">Column</th>
                            <th className="p-3 font-medium">Type</th>
                            <th className="p-3 font-medium">Missing</th>
                            <th className="p-3 font-medium">Unique</th>
                          </tr>
                        </thead>

                        <tbody>

                          {analysis.profile.columns.map((col) => (

                            <tr
                              key={col.name}
                              className="border-t border-slate-100 transition-colors hover:bg-slate-50"
                            >

                              <td className="p-3 font-medium text-slate-900">
                                {col.name}
                              </td>

                              <td className="p-3">
                                <span className="rounded-md bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
                                  {col.data_type}
                                </span>
                              </td>

                              <td className="p-3">
                                {col.missing_values}
                              </td>

                              <td className="p-3">
                                {col.unique_values}
                              </td>

                            </tr>

                          ))}

                        </tbody>

                      </table>

                    </div>
                  </div>

                </div>


                {/* ---------- Data Quality ---------- */}

                <div className={show("quality")}>
                  <QualityReport quality={analysis.quality} />
                </div>


                {/* ---------- Business Diagnostics ---------- */}

                <div className={`[&>section]:mt-0 ${show("diagnostics")}`}>
                  <BusinessDiagnostics
                    diagnostics={analysis.diagnostics}
                  />
                </div>


                {/* ---------- Analytics (filters + dashboard) ---------- */}

                <div className={`space-y-6 [&>section]:mt-0 ${show("analytics")}`}>

                  {/* Interactive Filters */}

                  <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">

                    <div className="mb-5 flex items-center gap-3">

                      <div className="rounded-lg bg-indigo-50 p-2 text-indigo-600">
                        <Filter size={20} />
                      </div>

                      <div>
                        <h3 className="font-semibold text-slate-900">
                          Dashboard Filters
                        </h3>

                        <p className="text-sm text-slate-500">
                          Filter your analytics by date and category.
                        </p>
                      </div>

                    </div>


                    <div className="grid grid-cols-1 gap-5 md:grid-cols-3">

                      {/* Start Date */}

                      {filterOptions?.date_column && (
                        <div>

                          <label className="mb-2 block text-sm font-medium text-slate-700">
                            Start Date
                          </label>

                          <input
                            type="date"
                            value={filters.startDate}
                            min={filterOptions.available_start_date || undefined}
                            max={filterOptions.available_end_date || undefined}
                            onChange={(e) =>
                              handleFilterChange("startDate", e.target.value)
                            }
                            className={inputClass}
                          />

                        </div>
                      )}


                      {/* End Date */}

                      {filterOptions?.date_column && (
                        <div>

                          <label className="mb-2 block text-sm font-medium text-slate-700">
                            End Date
                          </label>

                          <input
                            type="date"
                            value={filters.endDate}
                            min={filterOptions.available_start_date || undefined}
                            max={filterOptions.available_end_date || undefined}
                            onChange={(e) =>
                              handleFilterChange("endDate", e.target.value)
                            }
                            className={inputClass}
                          />

                        </div>
                      )}


                      {/* Category */}

                      {filterOptions?.category_column && (
                        <div>

                          <label className="mb-2 block text-sm font-medium text-slate-700">
                            {filterOptions.category_column}
                          </label>

                          <select
                            value={filters.category}
                            onChange={(e) =>
                              handleFilterChange("category", e.target.value)
                            }
                            className={inputClass}
                          >

                            <option value="All">
                              All Categories
                            </option>

                            {filterOptions.category_options?.map((option) => (
                              <option key={option} value={option}>
                                {option}
                              </option>
                            ))}

                          </select>

                        </div>
                      )}

                    </div>


                    {/* Filter Buttons */}

                    <div className="mt-6 flex flex-wrap items-center gap-3">

                      <button
                        onClick={handleApplyFilters}
                        disabled={loading}
                        className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-6 py-3 text-sm font-medium text-white shadow-sm transition hover:bg-indigo-700 disabled:opacity-50"
                      >

                        {loading ? (
                          <>
                            <Loader2 size={17} className="animate-spin" />
                            Applying...
                          </>
                        ) : (
                          "Apply Filters"
                        )}

                      </button>


                      <button
                        onClick={handleResetFilters}
                        disabled={loading}
                        className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-6 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
                      >

                        <RotateCcw size={16} />
                        Reset Filters

                      </button>

                    </div>


                    {filterError && (
                      <p className="mt-4 text-sm text-red-600">
                        {filterError}
                      </p>
                    )}


                    {/* Filtered Records */}

                    {analytics?.filters && (
                      <div className="mt-5 flex flex-wrap justify-between gap-2 border-t border-slate-100 pt-4">

                        <p className="text-sm text-slate-500">
                          Showing{" "}
                          <strong className="text-slate-800">
                            {analytics.filters.filtered_records}
                          </strong>{" "}
                          of{" "}
                          <strong className="text-slate-800">
                            {analytics.filters.total_records}
                          </strong>{" "}
                          records
                        </p>

                        {hasActiveFilters && (
                          <span className="text-xs font-medium text-indigo-600">
                            Filters selected
                          </span>
                        )}

                      </div>
                    )}

                  </div>


                  {/* Analytics Dashboard */}

                  {analytics?.filters?.filtered_records === 0 ? (

                    <div className="rounded-xl border border-amber-200 bg-white p-10 text-center shadow-sm">

                      <AlertTriangle
                        className="mx-auto mb-3 text-amber-500"
                        size={32}
                      />

                      <h3 className="font-semibold text-slate-800">
                        No matching records found
                      </h3>

                      <p className="mt-2 text-sm text-slate-500">
                        Try changing your date range or category selection.
                      </p>

                    </div>

                  ) : (
                    <AnalyticsDashboard analytics={analytics} />
                  )}

                </div>


                {/* ---------- Predictive ---------- */}

                <div className={show("predictive")}>
                  <PredictiveDashboard
                    forecast={analysis.forecast}
                    file={selectedFile}
                  />
                </div>


                {/* ---------- AI Assistant ---------- */}

                <div className={show("assistant")}>

                  {selectedFile ? (
                    <AIChat
                      key={`${selectedFile.name}-${selectedFile.lastModified}`}
                      file={selectedFile}
                    />
                  ) : isSavedAnalysis ? (
                    <div className="rounded-xl border border-blue-100 bg-blue-50 p-5">
                      <p className="text-sm text-blue-800">
                        AI chat and file-based filtering will be available for saved datasets after the backend is updated to load the stored file directly.
                      </p>
                    </div>
                  ) : null}

                </div>

              </div>
            )}

          </div>

        </main>

        <Footer />

      </div>

    </div>
  );
}

export default App;