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
    onResponseError({ response }) {
      const detail = response._data?.detail
      if (!Array.isArray(detail)) return

      const fields = [...new Set(detail
        .map(item => item?.loc?.at?.(-1))
        .filter((field): field is string => typeof field === 'string'))]
        .map(field => field.replaceAll('_', ' '))

      response._data.detail = fields.length
        ? `Please check the ${fields.join(', ')} field${fields.length > 1 ? 's' : ''} and try again.`
        : 'Some information is invalid. Please review the form and try again.'
    },
  })

  return {
    provide: {
      api,
    },
  }
})
