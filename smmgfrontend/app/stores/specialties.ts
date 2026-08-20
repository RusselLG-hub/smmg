import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useSpecialtiesService } from '~/services/specialties'
import type { Specialty, SpecialtyCreate, SpecialtyUpdate } from '~~/shared/types/Specialty'

export const useSpecialtiesStore = defineStore('specialties', () => {
  const specialties = ref<Specialty[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const specialtiesService = useSpecialtiesService()

  const fetchSpecialties = async (activeOnly = false) => {
    loading.value = true
    error.value = null
    try {
      specialties.value = await specialtiesService.getSpecialties(activeOnly)
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to fetch specialties'
    } finally {
      loading.value = false
    }
  }

  const createSpecialty = async (data: SpecialtyCreate) => {
    loading.value = true
    error.value = null
    try {
      const created = await specialtiesService.createSpecialty(data)
      specialties.value.push(created)
      return created
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to create specialty'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateSpecialty = async (id: string, data: SpecialtyUpdate) => {
    loading.value = true
    error.value = null
    try {
      const updated = await specialtiesService.updateSpecialty(id, data)
      const index = specialties.value.findIndex(s => s.id === id)
      if (index !== -1) {
        specialties.value[index] = updated
      }
      return updated
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to update specialty'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteSpecialty = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      await specialtiesService.deleteSpecialty(id)
      specialties.value = specialties.value.filter(s => s.id !== id)
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to delete specialty'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    specialties,
    loading,
    error,
    fetchSpecialties,
    createSpecialty,
    updateSpecialty,
    deleteSpecialty,
  }
})
