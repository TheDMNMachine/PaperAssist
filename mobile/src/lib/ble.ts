/**
 * BLE service for communicating with ESP32 PaperAssist device.
 *
 * Uses react-native-ble-plx. The ESP32 should expose a GATT service
 * with characteristics for reading status and writing commands.
 *
 * Service UUID and characteristic UUIDs should match the firmware BLE setup.
 */

import { BleManager, Device } from "react-native-ble-plx";

const SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb";
const CHAR_STATUS_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb";
const CHAR_COMMAND_UUID = "0000ffe2-0000-1000-8000-00805f9b34fb";

const DEVICE_NAME_PREFIX = "EPaper";

class BleService {
  private manager: BleManager;
  private device: Device | null = null;

  constructor() {
    this.manager = new BleManager();
  }

  async scan(onFound: (device: Device) => void, timeoutMs = 10000) {
    this.manager.startDeviceScan(null, null, (error, device) => {
      if (error) {
        console.error("BLE scan error:", error);
        return;
      }
      if (device?.name?.startsWith(DEVICE_NAME_PREFIX)) {
        onFound(device);
      }
    });

    setTimeout(() => this.manager.stopDeviceScan(), timeoutMs);
  }

  stopScan() {
    this.manager.stopDeviceScan();
  }

  async connect(deviceId: string): Promise<Device> {
    const device = await this.manager.connectToDevice(deviceId);
    await device.discoverAllServicesAndCharacteristics();
    this.device = device;
    return device;
  }

  async disconnect() {
    if (this.device) {
      await this.device.cancelConnection();
      this.device = null;
    }
  }

  async readStatus(): Promise<string | null> {
    if (!this.device) return null;
    const char = await this.device.readCharacteristicForService(
      SERVICE_UUID,
      CHAR_STATUS_UUID,
    );
    return char.value; // base64 encoded
  }

  async sendCommand(command: string): Promise<void> {
    if (!this.device) return;
    const base64 = btoa(command);
    await this.device.writeCharacteristicWithResponseForService(
      SERVICE_UUID,
      CHAR_COMMAND_UUID,
      base64,
    );
  }

  isConnected(): boolean {
    return this.device !== null;
  }
}

export const bleService = new BleService();
