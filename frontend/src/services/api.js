// src/services/api.js
import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000',
});

// Call the endpoint to find face vectors and matching faces by name
export const findSeltsivend = async (first, last) => {
    console.log("Otsime seltsivendasid api.js")
    try {
        const response = await api.get('/find', {
            params: { first, last },
        });
        return {
            photos: Array.isArray(response.data) ? response.data : [response.data]
        };
    } catch (error) {
        console.error('Error fetching seltsivend:', error);
        throw error;
    }
};

// Call the endpoint to find similar faces for a given face vector
export const findSimilar = async (params) => {
    console.log("Finding similars");
    try {
        const response = await api.get('/find_similar', {
            params: "face_vector" in params ? { face_vector: params.face_vector } : { first: params.first_name, last: params.last_name }
        });
        return {
            photos: Array.isArray(response.data) ? response.data : [response.data]
        };
    } catch (error) {
        console.error('Error fetching similar faces:', error);
        throw error;
    }
};