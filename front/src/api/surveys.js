import api from '@/api/auth'

export const getSurveys = () => api.get('/surveys/surveys/')
export const createSurvey = (data) => api.post('/surveys/surveys/', data)
export const getSurvey = (id) => api.get(`/surveys/surveys/${id}/`)
export const updateSurvey = (id, data) => api.put(`/surveys/surveys/${id}/`, data)
export const patchSurvey = (id, data) => api.patch(`/surveys/surveys/${id}/`, data)
export const deleteSurvey = (id) => api.delete(`/surveys/surveys/${id}/`)
export const submitSurveyResponse = (id, data) => api.post(`/surveys/surveys/${id}/respond/`, data)
