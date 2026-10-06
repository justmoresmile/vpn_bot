import { apiRequest } from './api'


export type TrialStatus = {
  available: boolean
  used: boolean
  active: boolean
  started_at: string | null
  ends_at: string | null
  remaining_seconds: number
  duration_days: number
}


export type TrialStartResponse = {
  status: string
  subscription_id: number
  trial_started_at: string
  trial_ends_at: string
  billing_mode: string
  billing_day_index: number
}


export async function getTrialStatus(): Promise<TrialStatus> {
  return apiRequest<TrialStatus>(
    '/trial/status',
  )
}


export async function startTrial(): Promise<TrialStartResponse> {
  return apiRequest<TrialStartResponse>(
    '/trial/start',
    {
      method: 'POST',
    },
  )
}


export type TrialFinishResponse =
  | {
      status: 'activated'
      subscription_id: number
      charged_kopecks: number
      balance_kopecks: number
      device_limit: number
      paid_until: string
    }
  | {
      status: 'insufficient_balance'
      required_kopecks: number
      balance_kopecks: number
      subscription_id: number
    }


export async function finishTrial(
  deviceLimit: number,
): Promise<TrialFinishResponse> {
  return apiRequest<TrialFinishResponse>(
    `/trial/finish?device_limit=${deviceLimit}`,
    {
      method: 'POST',
    },
  )
}
