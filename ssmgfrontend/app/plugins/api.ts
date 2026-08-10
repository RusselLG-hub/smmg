export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  const requestHeaders = import.meta.server
    ? useRequestHeaders(['cookie'])
    : undefined

  const api = $fetch.create({
    baseURL: import.meta.server
      ? config.apiInternalBaseUrl || config.public.apiBaseUrl
      : config.public.apiBaseUrl,
    credentials: 'include',
    headers: requestHeaders,
  })

  return {
    provide: {
      api,
    },
  }
})
