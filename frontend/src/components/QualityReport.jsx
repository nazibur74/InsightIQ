import {
  ShieldCheck,
  AlertTriangle,
  AlertCircle,
  Info,
  CheckCircle2
} from "lucide-react";

export default function QualityReport({ quality }) {

  if (!quality) return null;

  const score = quality.quality_score;

  const scoreLabel =
    score >= 90 ? "Excellent" :
    score >= 75 ? "Good" :
    score >= 50 ? "Needs Improvement" :
    "Poor";

  const scoreColor =
    score >= 90 ? "text-green-600" :
    score >= 75 ? "text-blue-600" :
    score >= 50 ? "text-amber-600" :
    "text-red-600";

  const severityConfig = {
    high: {
      label: "High",
      icon: AlertTriangle,
      color: "text-red-600",
      bg: "bg-red-50"
    },
    medium: {
      label: "Medium",
      icon: AlertCircle,
      color: "text-amber-600",
      bg: "bg-amber-50"
    },
    low: {
      label: "Low",
      icon: Info,
      color: "text-blue-600",
      bg: "bg-blue-50"
    }
  };

  return (
    <div className="space-y-6">

      {/* Quality Score */}
      <div className="bg-white border border-slate-200
        rounded-xl p-6">

        <div className="flex items-center gap-2 mb-5">
          <ShieldCheck className="text-blue-600" />
          <h3 className="font-semibold text-lg">
            Data Quality Assessment
          </h3>
        </div>

        <div className="flex flex-col md:flex-row
          md:items-center justify-between gap-6">

          <div>
            <p className="text-sm text-slate-500">
              Overall quality score
            </p>

            <h2 className={`text-5xl font-bold mt-2 ${scoreColor}`}>
              {score}/100
            </h2>

            <p className={`font-medium mt-2 ${scoreColor}`}>
              {scoreLabel}
            </p>
          </div>

          <div className="flex-1 max-w-md">
            <div className="h-3 bg-slate-100 rounded-full
              overflow-hidden">

              <div
                className="h-full bg-blue-600 rounded-full
                  transition-all"
                style={{ width: `${score}%` }}
              />
            </div>

            <p className="text-xs text-slate-500 mt-2">
              {quality.score_method}
            </p>
          </div>
        </div>
      </div>

      {/* Severity Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

        {Object.entries(severityConfig).map(
          ([key, config]) => {
            const Icon = config.icon;

            return (
              <div key={key}
                className="bg-white border border-slate-200
                  rounded-xl p-5">

                <div className={`w-10 h-10 rounded-lg
                  ${config.bg} flex items-center
                  justify-center`}>

                  <Icon className={config.color} />
                </div>

                <p className="text-sm text-slate-500 mt-4">
                  {config.label} Issues
                </p>

                <h3 className="text-2xl font-bold mt-1">
                  {quality.severity_counts[key]}
                </h3>
              </div>
            );
          }
        )}
      </div>

      {/* Issue List */}
      <div className="bg-white border border-slate-200
        rounded-xl p-6">

        <div className="flex justify-between
          items-center mb-5">

          <h3 className="font-semibold text-lg">
            Detected Data Issues
          </h3>

          <span className="text-sm text-slate-500">
            {quality.total_issues} findings
          </span>
        </div>

        {quality.issues.length === 0 ? (
          <div className="text-center py-10">
            <CheckCircle2
              size={42}
              className="mx-auto text-green-600"
            />

            <p className="font-medium mt-3">
              No issues detected
            </p>

            <p className="text-sm text-slate-500 mt-1">
              Your dataset passed all current quality checks.
            </p>
          </div>
        ) : (
          <div className="space-y-4">

            {quality.issues.map((issue, index) => {
              const config =
                severityConfig[issue.severity];

              const Icon = config.icon;

              return (
                <div key={`${issue.title}-${issue.column}-${index}`}
                  className="border border-slate-200
                    rounded-lg p-4">

                  <div className="flex justify-between
                    items-start gap-3">

                    <div className="flex gap-3">
                      <Icon
                        className={`${config.color} shrink-0`}
                        size={21}
                      />

                      <div>
                        <h4 className="font-semibold text-slate-800">
                          {issue.title}
                        </h4>

                        <p className="text-sm text-slate-500 mt-1">
                          {issue.description}
                        </p>

                        {issue.column && (
                          <p className="text-xs text-slate-400 mt-2">
                            Column: {issue.column}
                          </p>
                        )}

                        <p className="text-sm text-blue-700 mt-3">
                          Recommendation: {issue.recommendation}
                        </p>
                      </div>
                    </div>

                    <span className={`text-xs px-3 py-1
                      rounded-full ${config.bg}
                      ${config.color}`}>
                      {config.label}
                    </span>
                  </div>
                </div>
              );
            })}

          </div>
        )}
      </div>
    </div>
  );
}
