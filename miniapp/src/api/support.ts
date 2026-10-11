import {
  apiRequest,
} from './api'


export type SupportTicket = {
  id: number
  user_id: number
  subject: string
  category: string | null
  status: string
  created_at: string
  updated_at: string
  closed_at: string | null
}


export type SupportMessage = {
  id: number
  ticket_id: number
  sender_type: string
  sender_id: number | null
  message: string
  is_read: boolean
  created_at: string
}


export type SupportTicketDetails =
  SupportTicket & {
    messages: SupportMessage[]
  }


export async function getSupportTickets():
Promise<SupportTicket[]> {

  return apiRequest<SupportTicket[]>(
    '/support/tickets',
  )
}


export async function getSupportTicket(
  ticketId: number,
): Promise<SupportTicketDetails> {

  return apiRequest<SupportTicketDetails>(
    `/support/tickets/${ticketId}`,
  )
}


export async function createSupportTicket(
  subject: string,
  message: string,
  category?: string,
): Promise<SupportTicketDetails> {

  return apiRequest<SupportTicketDetails>(
    '/support/tickets',
    {
      method: 'POST',
      body: JSON.stringify({
        subject,
        message,
        category:
          category || null,
      }),
    },
  )
}


export async function sendSupportMessage(
  ticketId: number,
  message: string,
): Promise<SupportMessage> {

  return apiRequest<SupportMessage>(
    `/support/tickets/${ticketId}/messages`,
    {
      method: 'POST',
      body: JSON.stringify({
        message,
      }),
    },
  )
}


export async function closeSupportTicket(
  ticketId: number,
): Promise<SupportTicket> {

  return apiRequest<SupportTicket>(
    `/support/tickets/${ticketId}/close`,
    {
      method: 'POST',
    },
  )
}


export async function deleteSupportTicket(
  ticketId: number,
): Promise<{ success: boolean }> {

  return apiRequest<{ success: boolean }>(
    `/support/tickets/${ticketId}`,
    {
      method: 'DELETE',
    },
  )
}
