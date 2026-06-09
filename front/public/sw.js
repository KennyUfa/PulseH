self.addEventListener('push', event => {
  console.log('[SW] push received', event.data?.text())
  if (!event.data) return
  let data
  try { data = event.data.json() } catch { data = { title: 'PulseHR', body: event.data.text(), url: '/' } }
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: '/favicon.ico',
      badge: '/favicon.ico',
      data: { url: data.url, survey_id: data.survey_id },
      actions: [{ action: 'open', title: 'Пройти опрос' }],
    })
  )
})

self.addEventListener('notificationclick', event => {
  event.notification.close()
  const url = event.notification.data?.url || '/'
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(list => {
      for (const client of list) {
        if ('focus' in client) { client.focus(); client.navigate(url); return }
      }
      return clients.openWindow(url)
    })
  )
})
