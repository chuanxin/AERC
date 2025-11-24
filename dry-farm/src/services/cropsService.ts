import { apiService } from './api/http'
import { CROPS } from './api/endpoints'
import { ApplicationError } from '@/utils/asyncHelpers'

// Types for crops data
export interface CropCategory {
  id: number
  name: string
}

export interface CropName {
  id: number
  name: string
  category_id: number
}

export interface CropCategoryWithNames {
  id: number
  name: string
  crop_names: CropName[]
}

// API service functions
export const fetchAllCropCategories = async (): Promise<CropCategory[]> => {
  try {
    const response = await apiService.get<CropCategory[]>(CROPS.CATEGORIES)
    return response
  } catch (error: unknown) {
    if (error instanceof Error) {
      const status = (error as { response?: { status?: number } })?.response?.status || 0
      const message = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || error.message || 'Failed to load crop categories'

      throw new ApplicationError({
        message,
        status,
        source: 'cropsService.fetchAllCropCategories',
        originalError: error
      })
    } else {
      throw new ApplicationError({
        message: 'An unknown error occurred',
        status: 500,
        source: 'cropsService.fetchAllCropCategories',
        originalError: error
      })
    }
  }
}

export const fetchCropNamesByCategory = async (categoryId: number): Promise<CropName[]> => {
  try {
    const response = await apiService.get<CropName[]>(CROPS.NAMES_BY_CATEGORY(categoryId))
    return response
  } catch (error: unknown) {
    if (error instanceof Error) {
      const status = (error as { response?: { status?: number } })?.response?.status || 0
      const message = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || error.message || `Failed to load crop names for category ${categoryId}`

      throw new ApplicationError({
        message,
        status,
        source: 'cropsService.fetchCropNamesByCategory',
        originalError: error
      })
    } else {
      throw new ApplicationError({
        message: 'An unknown error occurred',
        status: 500,
        source: 'cropsService.fetchCropNamesByCategory',
        originalError: error
      })
    }
  }
}

export const fetchCropsGrouped = async (): Promise<CropCategoryWithNames[]> => {
  try {
    const response = await apiService.get<CropCategoryWithNames[]>(CROPS.GROUPED)
    return response
  } catch (error: unknown) {
    if (error instanceof Error) {
      const status = (error as { response?: { status?: number } })?.response?.status || 0
      const message = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || error.message || 'Failed to load grouped crops data'

      throw new ApplicationError({
        message,
        status,
        source: 'cropsService.fetchCropsGrouped',
        originalError: error
      })
    } else {
      throw new ApplicationError({
        message: 'An unknown error occurred',
        status: 500,
        source: 'cropsService.fetchCropsGrouped',
        originalError: error
      })
    }
  }
}

export const fetchCropsAsDict = async (): Promise<Record<string, string[]>> => {
  try {
    const response = await apiService.get<Record<string, string[]>>(CROPS.DICT)
    return response
  } catch (error: unknown) {
    if (error instanceof Error) {
      const status = (error as { response?: { status?: number } })?.response?.status || 0
      const message = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || error.message || 'Failed to load crops dictionary'

      throw new ApplicationError({
        message,
        status,
        source: 'cropsService.fetchCropsAsDict',
        originalError: error
      })
    } else {
      throw new ApplicationError({
        message: 'An unknown error occurred',
        status: 500,
        source: 'cropsService.fetchCropsAsDict',
        originalError: error
      })
    }
  }
}
