"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { DeviceStatus } from "@/types";

export default function SettingsPage() {
  const [device, setDevice] = useState<DeviceStatus | null>(null);
  const [deviceId, setDeviceId] = useState("esp32-main");
  const [error, setError] = useState<string | null>(null);

  const loadDevice = async () => {
    setError(null);
    try {
      const status = await api.device.status(deviceId);
      setDevice(status);
    } catch {
      setDevice(null);
      setError("Device not found or API unavailable");
    }
  };

  useEffect(() => {
    loadDevice();
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>

      <section className="rounded-lg border border-gray-800 bg-gray-900 p-6">
        <h2 className="mb-4 text-lg font-semibold text-gray-300">
          Device Status
        </h2>

        <div className="mb-4 flex gap-2">
          <input
            type="text"
            value={deviceId}
            onChange={(e) => setDeviceId(e.target.value)}
            className="rounded-md border border-gray-700 bg-gray-800 px-3 py-2 focus:border-rose-500 focus:outline-none"
            placeholder="Device ID"
          />
          <button
            onClick={loadDevice}
            className="rounded-md bg-gray-700 px-4 py-2 text-sm hover:bg-gray-600"
          >
            Refresh
          </button>
        </div>

        {error && <p className="text-sm text-red-400">{error}</p>}

        {device && (
          <div className="space-y-2 text-sm">
            <p>
              <span className="text-gray-400">Device ID:</span>{" "}
              {device.device_id}
            </p>
            <p>
              <span className="text-gray-400">IP:</span> {device.ip_address}
            </p>
            <p>
              <span className="text-gray-400">Firmware:</span>{" "}
              {device.firmware_version}
            </p>
            <p>
              <span className="text-gray-400">Battery:</span>{" "}
              {device.battery_level ?? "N/A"}%
            </p>
            <p>
              <span className="text-gray-400">Last seen:</span>{" "}
              {new Date(device.last_seen).toLocaleString()}
            </p>
          </div>
        )}
      </section>

      <section className="rounded-lg border border-gray-800 bg-gray-900 p-6">
        <h2 className="mb-4 text-lg font-semibold text-gray-300">API Info</h2>
        <p className="text-sm text-gray-400">
          Base URL:{" "}
          <code className="rounded bg-gray-800 px-2 py-0.5">
            {process.env.NEXT_PUBLIC_API_URL || "/api"}
          </code>
        </p>
      </section>
    </div>
  );
}
