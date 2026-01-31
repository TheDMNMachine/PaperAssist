const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://paperassist.tojest.dev/api";

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
    list: () => request<import("@/types").Screen[]>("/screens"),
    getCurrent: () =>
      request<import("@/types").Screen | null>("/screens/current"),
    get: (id: string) => request<import("@/types").Screen>(`/screens/${id}`),
    create: (data: Partial<import("@/types").Screen>) =>
      request<import("@/types").Screen>("/screens", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    update: (id: string, data: Partial<import("@/types").Screen>) =>
      request<import("@/types").Screen>(`/screens/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      request<void>(`/screens/${id}`, { method: "DELETE" }),
  },
  alarms: {
    list: () => request<import("@/types").Alarm[]>("/alarms"),
    getActive: () => request<import("@/types").Alarm[]>("/alarms/active"),
    create: (data: Partial<import("@/types").Alarm>) =>
      request<import("@/types").Alarm>("/alarms", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    update: (id: string, data: Partial<import("@/types").Alarm>) =>
      request<import("@/types").Alarm>(`/alarms/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      request<void>(`/alarms/${id}`, { method: "DELETE" }),
  },
  device: {
    status: (deviceId: string) =>
      request<import("@/types").DeviceStatus>(`/device/status/${deviceId}`),
    heartbeat: (data: {
      device_id: string;
      ip_address?: string;
      firmware_version?: string;
      battery_level?: number;
    }) =>
      request<import("@/types").DeviceStatus>("/device/heartbeat", {
        method: "POST",
        body: JSON.stringify(data),
      }),
  },
};
