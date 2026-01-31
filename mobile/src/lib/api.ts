import type { Screen, Alarm, DeviceStatus } from "@/types";

const API_BASE = "http://paperassist.tojest.dev/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}/v1${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  screens: {
    list: () => request<Screen[]>("/screens"),
    getCurrent: () => request<Screen | null>("/screens/current"),
    get: (id: string) => request<Screen>(`/screens/${id}`),
    create: (data: Partial<Screen>) =>
      request<Screen>("/screens", { method: "POST", body: JSON.stringify(data) }),
    update: (id: string, data: Partial<Screen>) =>
      request<Screen>(`/screens/${id}`, { method: "PUT", body: JSON.stringify(data) }),
    delete: (id: string) => request<void>(`/screens/${id}`, { method: "DELETE" }),
  },
  alarms: {
    list: () => request<Alarm[]>("/alarms"),
    getActive: () => request<Alarm[]>("/alarms/active"),
    create: (data: Partial<Alarm>) =>
      request<Alarm>("/alarms", { method: "POST", body: JSON.stringify(data) }),
    update: (id: string, data: Partial<Alarm>) =>
      request<Alarm>(`/alarms/${id}`, { method: "PUT", body: JSON.stringify(data) }),
    delete: (id: string) => request<void>(`/alarms/${id}`, { method: "DELETE" }),
  },
  device: {
    status: (deviceId: string) => request<DeviceStatus>(`/device/status/${deviceId}`),
    heartbeat: (data: {
      device_id: string;
      ip_address?: string;
      firmware_version?: string;
      battery_level?: number;
    }) => request<DeviceStatus>("/device/heartbeat", { method: "POST", body: JSON.stringify(data) }),
  },
};
