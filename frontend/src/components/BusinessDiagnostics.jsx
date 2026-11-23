import {
  AlertTriangle,
  AlertCircle,
  CheckCircle2,
  Lightbulb,
  TrendingUp,
  BriefcaseBusiness
} from "lucide-react";

const severityStyles = {
  high: {
    color: "text-red-600",
    background: "bg-red-50",
    border: "border-red-200"
  },
  medium: {
    color: "text-amber-600",
    background: "bg-amber-50",
    border: "border-amber-200"
  },
  low: {
    color: "text-blue-600",
    background: "bg-blue-50",
    border: "border-blue-200"
  }
};

function BusinessDiagnostics({ diagnostics }) {
  if (!diagnostics) return null;

  const {
    detected_domain,
    column_mapping,
    total_findings,
    severity_counts,
    findings,
    method
  } = diagnostics;

  const hasFindings = findings && findings.length > 0;

  return (
    <section className="mt-8 space-y-6">

      {/* Section Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">

        <div>
          <div className="flex items-center gap-2">
            <TrendingUp className="text-indigo-600" size={24} />
            <h2 className="text-xl font-bold text-gray-900">
              Business Diagnostics
            </h2>
          </div>

          <p className="mt-1 text-sm text-gray-500">
            Automatically detected business insights and potential problems.
          </p>
        </div>

        <span className="w-fit rounded-full bg-indigo-50 px-4 py-2 text-sm font-medium text-indigo-700">
          {detected_domain}
        </span>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">

        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <p className="text-sm text-gray-500">Total Findings</p>
          <h3 className="mt-2 text-3xl font-bold text-gray-900">
            {total_findings}
          </h3>
        </div>

        <div className="rounded-xl border border-red-100 bg-white p-5">
          <p className="text-sm text-gray-500">High Severity</p>
          <h3 className="mt-2 text-3xl font-bold text-red-600">
            {severity_counts?.high || 0}
          </h3>
        </div>

        <div className="rounded-xl border border-amber-100 bg-white p-5">
          <p className="text-sm text-gray-500">Medium Severity</p>
          <h3 className="mt-2 text-3xl font-bold text-amber-600">
            {severity_counts?.medium || 0}
          </h3>
        </div>

        <div className="rounded-xl border border-blue-100 bg-white p-5">
          <p className="text-sm text-gray-500">Low Severity</p>
          <h3 className="mt-2 text-3xl font-bold text-blue-600">
            {severity_counts?.low || 0}
          </h3>
        </div>

      </div>

      {/* Detected Column Mapping */}
      <div className="rounded-xl border border-gray-200 bg-white p-5">

        <div className="mb-4 flex items-center gap-2">
          <BriefcaseBusiness size={20} className="text-indigo-600" />
          <h3 className="font-semibold text-gray-900">
            Detected Business Structure
          </h3>
        </div>

        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">

          {Object.entries(column_mapping || {}).map(([role, column]) => (
            <div
              key={role}
              className="rounded-lg bg-gray-50 p-3"
            >
              <p className="text-xs capitalize text-gray-500">
                {role.replace("_", " ")}
              </p>

              <p className="mt-1 break-words font-medium text-gray-900">
                {column}
              </p>
            </div>
          ))}

        </div>
      </div>

      {/* Findings */}
      <div className="rounded-xl border border-gray-200 bg-white p-5">

        <h3 className="mb-5 font-semibold text-gray-900">
          Detected Business Findings
        </h3>

        {!hasFindings ? (
          <div className="rounded-xl bg-green-50 p-6 text-center">

            <CheckCircle2
              size={36}
              className="mx-auto text-green-600"
            />

            <h4 className="mt-3 font-semibold text-green-800">
              No Business Issues Detected
            </h4>

            <p className="mx-auto mt-2 max-w-lg text-sm text-green-700">
              The diagnostic engine did not identify any issues
              using its current rules. This does not guarantee
              that the business has no underlying problems.
            </p>

          </div>
        ) : (
          <div className="space-y-4">

            {findings.map((finding, index) => {

              const style =
                severityStyles[finding.severity] ||
                severityStyles.low;

              return (
                <div
                  key={index}
                  className={`rounded-xl border p-5 ${style.border} ${style.background}`}
                >

                  <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">

                    <div className="flex items-start gap-3">

                      <AlertTriangle
                        size={21}
                        className={`${style.color} mt-1 shrink-0`}
                      />

                      <div>
                        <h4 className="font-semibold text-gray-900">
                          {finding.title}
                        </h4>

                        <p className="mt-2 text-sm text-gray-700">
                          {finding.description}
                        </p>
                      </div>

                    </div>

                    <span className={`w-fit rounded-full bg-white px-3 py-1 text-xs font-semibold uppercase ${style.color}`}>
                      {finding.severity}
                    </span>

                  </div>

                  {finding.metric && (
                    <div className="mt-4 text-sm text-gray-700">
                      <span className="font-medium">Metric:</span>{" "}
                      {finding.metric}
                      {finding.value !== null &&
                        finding.value !== undefined && (
                          <span> — {finding.value}</span>
                        )}
                    </div>
                  )}

                  {finding.evidence &&
                    Object.keys(finding.evidence).length > 0 && (
                      <div className="mt-3 rounded-lg bg-white/70 p-3">
                        <p className="mb-2 text-xs font-semibold uppercase text-gray-500">
                          Supporting Evidence
                        </p>

                        {Object.entries(finding.evidence).map(
                          ([key, value]) => (
                            <div
                              key={key}
                              className="flex flex-wrap justify-between gap-2 py-1 text-sm"
                            >
                              <span className="text-gray-600">
                                {key.replaceAll("_", " ")}
                              </span>

                              <span className="font-medium text-gray-900">
                                {String(value)}
                              </span>
                            </div>
                          )
                        )}
                      </div>
                    )}

                  <div className="mt-4 flex items-start gap-2 rounded-lg bg-white/70 p-3">
                    <Lightbulb
                      size={18}
                      className="mt-0.5 shrink-0 text-amber-600"
                    />

                    <p className="text-sm text-gray-700">
                      <span className="font-semibold">
                        Recommendation:{" "}
                      </span>
                      {finding.recommendation}
                    </p>
                  </div>

                </div>
              );
            })}

          </div>
        )}

      </div>

      {/* Methodology */}
      <div className="flex items-start gap-2 rounded-lg bg-gray-50 p-4">
        <AlertCircle
          size={18}
          className="mt-0.5 shrink-0 text-gray-500"
        />

        <p className="text-xs leading-5 text-gray-500">
          {method}
        </p>
      </div>

    </section>
  );
}

export default BusinessDiagnostics;
