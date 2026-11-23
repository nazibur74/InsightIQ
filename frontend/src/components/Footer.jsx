import { Activity, Code2, ShieldCheck } from "lucide-react";

function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl flex-col gap-4 px-4 py-6 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-10">

        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-indigo-600 p-1.5 text-white">
            <Activity size={16} />
          </div>

          <div>
            <p className="text-sm font-semibold text-slate-800">
              InsightIQ
            </p>
            <p className="text-xs text-slate-500">
              AI-powered automated data analytics platform
            </p>
          </div>
        </div>

        <p className="flex items-center gap-1.5 text-xs text-slate-500">
          <ShieldCheck size={14} className="shrink-0 text-slate-400" />
          Review storage and retention before uploading sensitive data.
        </p>

        <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-xs text-slate-500">
          <span>
            Built with React, FastAPI &amp; Gemini
          </span>

          <a
            href="https://github.com/nazibur74"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 font-medium text-slate-600 transition hover:text-indigo-600"
          >
            <Code2 size={14} />
            nazibur74
          </a>

          <span>
            &copy; {year} Md. Nazibur Rahman
          </span>
        </div>

      </div>
    </footer>
  );
}

export default Footer;