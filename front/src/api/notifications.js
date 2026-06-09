import api from '@/api/auth'

export const getVapidKey = () => api.get('/notifications/push/vapid-key/')
export const saveSubscription = (data) => api.post('/notifications/push/subscribe/', data)
export const deleteSubscription = (endpoint) => api.delete('/notifications/push/unsubscribe/', { data: { endpoint } })
