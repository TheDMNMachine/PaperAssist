import { useState } from "react";
import { View, Text, ScrollView, TouchableOpacity } from "react-native";
import { bleService } from "@/lib/ble";

interface FoundDevice {
  id: string;
  name: string | null;
}

export default function BluetoothScreen() {
  const [scanning, setScanning] = useState(false);
  const [devices, setDevices] = useState<FoundDevice[]>([]);
  const [connected, setConnected] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  const startScan = async () => {
    setScanning(true);
    setDevices([]);
    await bleService.scan((device) => {
      setDevices((prev) => {
        if (prev.some((d) => d.id === device.id)) return prev;
        return [...prev, { id: device.id, name: device.name }];
      });
    });
    setTimeout(() => setScanning(false), 10000);
  };

  const connectToDevice = async (deviceId: string) => {
    try {
      await bleService.connect(deviceId);
      setConnected(true);
      const s = await bleService.readStatus();
      setStatus(s);
    } catch (e) {
      console.error("BLE connect error:", e);
    }
  };

  const disconnect = async () => {
    await bleService.disconnect();
    setConnected(false);
    setStatus(null);
  };

  const sendRefresh = async () => {
    await bleService.sendCommand("REFRESH");
  };

  return (
    <ScrollView
      style={{ flex: 1, backgroundColor: "#030712" }}
      contentContainerStyle={{ padding: 16, gap: 16 }}
    >
      <Text style={{ color: "#f9fafb", fontSize: 24, fontWeight: "bold" }}>
        Bluetooth
      </Text>

      {!connected ? (
        <>
          <TouchableOpacity
            onPress={startScan}
            disabled={scanning}
            style={{
              backgroundColor: scanning ? "#1f2937" : "#e11d48",
              borderRadius: 12,
              padding: 16,
              alignItems: "center",
            }}
          >
            <Text style={{ color: "#fff", fontWeight: "600" }}>
              {scanning ? "Scanning..." : "Scan for EPaper devices"}
            </Text>
          </TouchableOpacity>

          {devices.map((device) => (
            <TouchableOpacity
              key={device.id}
              onPress={() => connectToDevice(device.id)}
              style={{
                backgroundColor: "#111827",
                borderRadius: 12,
                padding: 16,
                borderWidth: 1,
                borderColor: "#1f2937",
              }}
            >
              <Text style={{ color: "#f9fafb", fontWeight: "600" }}>
                {device.name || "Unknown"}
              </Text>
              <Text style={{ color: "#6b7280", fontSize: 12 }}>
                {device.id}
              </Text>
            </TouchableOpacity>
          ))}

          {!scanning && devices.length === 0 && (
            <Text style={{ color: "#4b5563" }}>
              No devices found. Make sure your EPaper device is powered on.
            </Text>
          )}
        </>
      ) : (
        <>
          <View
            style={{
              backgroundColor: "#14532d",
              borderRadius: 12,
              padding: 16,
            }}
          >
            <Text style={{ color: "#86efac", fontWeight: "600" }}>
              Connected
            </Text>
            {status && (
              <Text style={{ color: "#bbf7d0", marginTop: 4, fontSize: 12 }}>
                Status: {status}
              </Text>
            )}
          </View>

          <TouchableOpacity
            onPress={sendRefresh}
            style={{
              backgroundColor: "#1d4ed8",
              borderRadius: 12,
              padding: 16,
              alignItems: "center",
            }}
          >
            <Text style={{ color: "#fff", fontWeight: "600" }}>
              Force Refresh Screen
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            onPress={disconnect}
            style={{
              backgroundColor: "#450a0a",
              borderRadius: 12,
              padding: 16,
              alignItems: "center",
            }}
          >
            <Text style={{ color: "#fca5a5", fontWeight: "600" }}>
              Disconnect
            </Text>
          </TouchableOpacity>
        </>
      )}
    </ScrollView>
  );
}
