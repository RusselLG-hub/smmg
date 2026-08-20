export interface UploadResponse {
  object_name: string
  url: string
}

export const useUploadService = () => {
  const { $api } = useNuxtApp()

  return {
    uploadImage: (file: File) => {
      const formData = new FormData()
      formData.append('file', file)

      return $api<UploadResponse>('/v1/uploads/image', {
        method: 'POST',
        body: formData,
      })
    },
  }
}
