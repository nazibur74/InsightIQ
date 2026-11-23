
import { useRef, useState } from "react";
import {
  UploadCloud,
  FileSpreadsheet,
  Loader2,
  X,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";
import { uploadDataset } from "../services/api";

const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20 MB

const ALLOWED_EXTENSIONS = [".xlsx", ".xls", ".csv"];

export default function FileUploader({ onSuccess }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef(null);

  const formatFileSize = (bytes) => {
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];

    if (!selectedFile) return;

    setError("");

    const extension = selectedFile.name
      .substring(selectedFile.name.lastIndexOf("."))
      .toLowerCase();

    if (!ALLOWED_EXTENSIONS.includes(extension)) {
      setFile(null);
      setError("Unsupported file type. Please select CSV or Excel.");
      event.target.value = "";
      return;
    }

    if (selectedFile.size > MAX_FILE_SIZE) {
      setFile(null);
      setError("File size exceeds the 20 MB limit.");
      event.target.value = "";
      return;
    }

    if (selectedFile.size === 0) {
      setFile(null);
      setError("The selected file is empty.");
      event.target.value = "";
      return;
    }

    setFile(selectedFile);
  };

  const removeFile = () => {
    if (loading) return;

    setFile(null);
    setError("");

    if (inputRef.current) {
      inputRef.current.value = "";
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select an Excel or CSV file.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const result = await uploadDataset(file);

      onSuccess(result, file);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        "Upload failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-8 shadow-sm">

      <div className="text-center">

        <div className="w-16 h-16 mx-auto mb-4 rounded-2xl
          bg-blue-50 flex items-center justify-center">
          <UploadCloud size={34} className="text-blue-600" />
        </div>

        <h2 className="text-xl font-semibold text-slate-800">
          Upload your dataset
        </h2>

        <p className="text-sm text-slate-500 mt-2">
          Upload an Excel or CSV file to start automated analysis.
        </p>

        <label
          htmlFor="dataset-upload"
          className={`mt-6 block border-2 border-dashed
            rounded-xl p-8 transition-colors
            ${loading
              ? "opacity-60 cursor-not-allowed"
              : "cursor-pointer hover:border-blue-500 hover:bg-blue-50/30"
            }
            ${file ? "border-green-400 bg-green-50/30" : "border-slate-300"}
          `}
        >
          <FileSpreadsheet
            size={36}
            className={`mx-auto ${file ? "text-green-600" : "text-slate-400"}`}
          />

          {file ? (
            <>
              <p className="mt-3 text-sm font-medium text-slate-700 break-all">
                {file.name}
              </p>

              <p className="text-xs text-slate-500 mt-1">
                {formatFileSize(file.size)}
              </p>
            </>
          ) : (
            <>
              <p className="mt-3 text-sm font-medium text-slate-700">
                Choose your dataset
              </p>

              <p className="text-xs text-slate-500 mt-1">
                CSV, XLSX or XLS · Maximum 20 MB
              </p>
            </>
          )}

          <input
            ref={inputRef}
            id="dataset-upload"
            type="file"
            accept=".xlsx,.xls,.csv"
            disabled={loading}
            className="sr-only"
            onChange={handleFileChange}
          />
        </label>

        {file && (
          <button
            type="button"
            onClick={removeFile}
            disabled={loading}
            className="mt-3 text-sm text-red-500 hover:text-red-700
              inline-flex items-center gap-1 disabled:opacity-50"
          >
            <X size={15} />
            Remove file
          </button>
        )}

        <button
          type="button"
          onClick={handleUpload}
          disabled={loading || !file}
          className="mt-5 px-8 py-3 rounded-lg
            bg-blue-600 text-white font-medium
            hover:bg-blue-700 disabled:opacity-50
            disabled:cursor-not-allowed
            inline-flex items-center justify-center gap-2
            transition-colors"
        >
          {loading ? (
            <>
              <Loader2 className="animate-spin" size={18} />
              Analyzing dataset...
            </>
          ) : (
            <>
              <CheckCircle2 size={18} />
              Analyze Dataset
            </>
          )}
        </button>

        {error && (
          <div
            role="alert"
            className="mt-4 p-3 rounded-lg bg-red-50
              border border-red-100 text-red-600
              text-sm flex items-start gap-2 text-left"
          >
            <AlertCircle size={17} className="shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <p className="text-xs text-slate-400 mt-5">
          Your dataset will be processed for automated analytics.
        </p>

      </div>
    </div>
  );
}
