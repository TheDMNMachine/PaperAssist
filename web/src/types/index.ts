export type ScreenType = "text" | "weather" | "calendar" | "custom";

export interface Screen {
  id: string;
  title: string;
  content: string;
  screen_type: ScreenType;
  is_active: boolean;
  display_order: number;
  created_at: string;
  updated_at: string;
}

export type AlarmStatus = "active" | "disabled" | "triggered";

export interface Alarm {
  id: string;
  name: string;
  trigger_time: string;
  message: string;
  status: AlarmStatus;
  repeat_days: number[];
  created_at: string;
  updated_at: string;
}

export interface DeviceStatus {
  id: string;
  device_id: string;
  ip_address: string;
  firmware_version: string;
  battery_level: number | null;
  last_seen: string;
}
