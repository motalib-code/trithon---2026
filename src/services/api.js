import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getDashboardStats = async () => {
    try {
        const response = await api.get('/dashboard/stats');
        return response.data;
    } catch (error) {
        console.error('Error fetching dashboard stats:', error);
        return null; // Fallback handled in component
    }
};

export const uploadScan = async (file, userName = 'Farmer', lang = 'en') => {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await api.post(`/scan/upload?user_name=${userName}&lang=${lang}`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        console.error('Error uploading scan:', error);
        throw error;
    }
};

export const getMapLayers = async (scanId) => {
    try {
        const response = await api.get(`/map/layers/${scanId}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching map layers:', error);
        return null;
    }
};

export const chatWithKisan = async (query, userName = 'Farmer') => {
    try {
        const response = await api.post('/chat', { query, user_name: userName });
        return response.data;
    } catch (error) {
        console.error('Error in Kisan Chatbot:', error);
        throw error;
    }
};

export default api;
