import { apiJson } from "./apiClient";

export type ChatResponse = { response: string };

export async function sendChatMessage(message: string): Promise<ChatResponse> {
  return apiJson<ChatResponse>("/chat", {
    method: "POST",
    body: { message },
  });
}
