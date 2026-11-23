import {
  Activity,
  LayoutDashboard,
  ShieldCheck,
  Stethoscope,
  BarChart3,
  TrendingUp,
  Sparkles,
  History,
  FileSpreadsheet,
  UploadCloud,
  X,
  Lock
} from "lucide-react";

// Single source of truth for navigation + page titles.
export const NAV_ITEMS = [
  {
    id: "overview",
    label: "Overview",
    icon: LayoutDashboard,
    section: "Workspace",
    requiresAnalysis: false,
    description: "Upload a dataset and review its structure."
  },
  {
    id: "quality",
    label: "Data Quality",
    icon: ShieldCheck,
    section: "Workspace",
    requiresAnalysis: true,
    description: "Quality score, missing values and detected data issues."
  },
  {
    id: "diagnostics",
    label: "Diagnostics",
    icon: Stethoscope,
    section: "Workspace",
    requiresAnalysis: true,
    description: "Automatically detected business findings and recommendations."
  },
  {
    id: "analytics",
    label: "Analytics",
    icon: BarChart3,
    section: "Workspace",
    requiresAnalysis: true,
    description: "Filter your data and explore KPIs, trends and categories."
  },
  {
    id: "predictive",
    label: "Predictive",
    icon: TrendingUp,
    section: "Workspace",
    requiresAnalysis: true,
    description: "Forecast future performance from historical trends."
  },
  {
    id: "assistant",
    label: "AI Assistant",
    icon: Sparkles,
    section: "Workspace",
    requiresAnalysis: true,
    description: "Ask questions about your dataset in plain language."
  },
  {
    id: "history",
    label: "Analysis History",
    icon: History,
    section: "Records",
    requiresAnalysis: false,
    description: "Access and manage your previously analyzed datasets."
  }
];

function Sidebar({
  activeView,
  onNavigate,
  hasAnalysis,
  filename,
  isSavedAnalysis,
  onNewUpload,
  mobileOpen,
  onClose
}) {
  const sections = ["Workspace", "Records"];

  const go = (id) => {
    onNavigate(id);
    onClose();
  };

  return (
    <>
      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/60 backdrop-blur-sm lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-72 flex-col
          bg-slate-900 text-slate-300 shadow-xl transition-transform duration-200
          lg:translate-x-0
          ${mobileOpen ? "translate-x-0" : "-translate-x-full"}`}
        aria-label="Primary navigation"
      >
        {/* Brand */}
        <div className="flex items-center justify-between px-6 py-6">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-gradient-to-br from-indigo-500 to-blue-600 p-2.5 text-white shadow-lg shadow-indigo-900/40">
              <Activity size={22} />
            </div>

            <div>
              <h1 className="text-lg font-bold leading-tight text-white">
                InsightIQ
              </h1>
              <p className="text-xs text-slate-400">
                AI-Powered Data Analyst
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white lg:hidden"
            aria-label="Close menu"
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-4 pb-4">
          {sections.map((section) => (
            <div key={section} className="mb-6">
              <p className="mb-2 px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                {section}
              </p>

              <ul className="space-y-1">
                {NAV_ITEMS.filter((item) => item.section === section).map(
                  (item) => {
                    const Icon = item.icon;
                    const active = activeView === item.id;
                    const locked = item.requiresAnalysis && !hasAnalysis;

                    return (
                      <li key={item.id}>
                        <button
                          type="button"
                          onClick={() => go(item.id)}
                          disabled={locked}
                          aria-current={active ? "page" : undefined}
                          title={
                            locked
                              ? "Upload a dataset to unlock this section"
                              : item.label
                          }
                          className={`group flex w-full items-center gap-3 rounded-lg px-3 py-2.5
                            text-sm font-medium transition
                            ${
                              active
                                ? "bg-indigo-600 text-white shadow-md shadow-indigo-900/30"
                                : locked
                                ? "cursor-not-allowed text-slate-600"
                                : "hover:bg-slate-800 hover:text-white"
                            }`}
                        >
                          <Icon size={18} className="shrink-0" />
                          <span className="flex-1 text-left">{item.label}</span>
                          {locked && <Lock size={13} className="shrink-0" />}
                        </button>
                      </li>
                    );
                  }
                )}
              </ul>
            </div>
          ))}
        </nav>

        {/* Active dataset */}
        <div className="border-t border-slate-800 p-4">
          {hasAnalysis ? (
            <div className="rounded-xl bg-slate-800/70 p-4">
              <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                Active dataset
              </p>

              <div className="mt-2 flex items-start gap-2">
                <FileSpreadsheet
                  size={18}
                  className="mt-0.5 shrink-0 text-indigo-400"
                />
                <p className="break-all text-sm font-medium text-white">
                  {filename}
                </p>
              </div>

              {isSavedAnalysis && (
                <p className="mt-2 text-xs text-slate-400">
                  Viewing saved analysis
                </p>
              )}

              <button
                type="button"
                onClick={() => {
                  onNewUpload();
                  onClose();
                }}
                className="mt-3 inline-flex w-full items-center justify-center gap-2 rounded-lg
                  border border-slate-600 px-3 py-2 text-xs font-medium text-slate-200
                  transition hover:bg-slate-700"
              >
                <UploadCloud size={15} />
                Upload another file
              </button>
            </div>
          ) : (
            <div className="rounded-xl bg-slate-800/50 p-4">
              <p className="text-sm font-medium text-slate-200">
                No dataset loaded
              </p>
              <p className="mt-1 text-xs text-slate-400">
                Upload a CSV or Excel file to unlock all analysis tools.
              </p>
            </div>
          )}
        </div>
      </aside>
    </>
  );
}

export default Sidebar;