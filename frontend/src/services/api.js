import axios from "axios";

const api = axios.create({
    baseURL: "http://127.0.0.1:8000/api",
});

// Upload dataset
export const uploadDataset = async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post("/upload", formData);
    return response.data;
};

// Apply analytics filters
export const filterDatasetAnalytics = async (file, filters) => {
    const formData = new FormData();
    formData.append("file", file);

    if (filters.startDate) {
        formData.append("start_date", filters.startDate);
    }

    if (filters.endDate) {
        formData.append("end_date", filters.endDate);
    }

    if (filters.category && filters.category !== "All") {
        formData.append("category_value", filters.category);
    }

    const response = await api.post("/analytics/filter", formData);
    return response.data;
};

// Ask AI about uploaded dataset
export const askDatasetAI = async (file, question) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("question", question);

    const response = await api.post("/ai/ask", formData);
    return response.data;
};

// Generate AI-powered predictive insights
export const generatePredictiveInsights = async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post(
        "/ai/predictive-insights",
        formData
    );

    return response.data;
};

// Generate and download PDF report
export const generatePdfReport = async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    return api.post("/reports/pdf", formData, {
        responseType: "blob",
    });
};

// Analysis History APIs
export const getAnalysisHistory = async (skip = 0, limit = 20) => {
    const response = await api.get("/history", {
        params: { skip, limit }
    });

    return response.data;
};

export const getDatasetDetails = async (datasetId) => {
    const response = await api.get(`/history/${datasetId}`);
    return response.data;
};

export const getSavedAnalysis = async (datasetId) => {
    const response = await api.get(
        `/history/${datasetId}/analysis`
    );

    return response.data;
};

export const deleteDatasetHistory = async (datasetId) => {
    const response = await api.delete(`/history/${datasetId}`);
    return response.data;
};

export default api;