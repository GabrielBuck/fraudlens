import type { Alert, Overview } from "./types";

const browserBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const serverBase = process.env.API_INTERNAL_URL ?? browserBase;

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${serverBase}${path}`, {
    next: { revalidate: 30 },
  });
  if (!response.ok)
    throw new Error(`Falha ao carregar ${path}: ${response.status}`);
  return response.json() as Promise<T>;
}

export async function browserApi<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(`${browserBase}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) throw new Error("Não foi possível concluir a ação.");
  return response.json() as Promise<T>;
}

export const getOverview = () => apiGet<Overview>("/api/v1/overview");
export const getAlert = (id: string) => apiGet<Alert>(`/api/v1/alerts/${id}`);
