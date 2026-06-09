import { getVapidKey, saveSubscription, deleteSubscription } from '@/api/notifications'

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const raw = atob(base64)
  return Uint8Array.from([...raw].map(c => c.charCodeAt(0)))
}

export async function registerServiceWorker() {
  if (!('serviceWorker' in navigator)) return null
  return navigator.serviceWorker.register('/sw.js')
}

export async function subscribeToPush() {
  if (!('PushManager' in window)) throw new Error('Push API не поддерживается')
  const reg = await registerServiceWorker()
  if (!reg) throw new Error('Service Worker не зарегистрирован')
  const { data } = await getVapidKey()
  const applicationServerKey = urlBase64ToUint8Array(data.public_key)
  const subscription = await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey })
  const json = subscription.toJSON()
  await saveSubscription({ endpoint: json.endpoint, p256dh: json.keys.p256dh, auth: json.keys.auth })
  return subscription
}

export async function unsubscribeFromPush() {
  if (!('serviceWorker' in navigator)) return
  const reg = await navigator.serviceWorker.getRegistration('/sw.js')
  if (!reg) return
  const sub = await reg.pushManager.getSubscription()
  if (!sub) return
  await deleteSubscription(sub.endpoint)
  await sub.unsubscribe()
}

export async function getPushPermission() {
  if (!('Notification' in window)) return 'unsupported'
  return Notification.permission
}
