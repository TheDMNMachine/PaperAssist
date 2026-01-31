import { useEffect, useState } from "react";
import { View, Text, ScrollView, TouchableOpacity, Alert } from "react-native";
import { api } from "@/lib/api";
import type { Alarm } from "@/types";

export default function AlarmsScreen() {
  const [alarms, setAlarms] = useState<Alarm[]>([]);

  const load = async () => {
    try {
      setAlarms(await api.alarms.list());
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const deleteAlarm = (alarm: Alarm) => {
    Alert.alert("Delete", `Delete "${alarm.name}"?`, [
      { text: "Cancel", style: "cancel" },
      {
        text: "Delete",
        style: "destructive",
        onPress: async () => {
          await api.alarms.delete(alarm.id);
          load();
        },
      },
    ]);
  };

  return (
    <ScrollView
      style={{ flex: 1, backgroundColor: "#030712" }}
      contentContainerStyle={{ padding: 16, gap: 12 }}
    >
      <Text style={{ color: "#f9fafb", fontSize: 24, fontWeight: "bold" }}>
        Alarms
      </Text>

      {alarms.map((alarm) => (
        <View
          key={alarm.id}
          style={{
            backgroundColor: "#111827",
            borderRadius: 12,
            padding: 16,
            borderWidth: 1,
            borderColor: "#1f2937",
          }}
        >
          <View
            style={{
              flexDirection: "row",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <Text
              style={{ color: "#f9fafb", fontSize: 16, fontWeight: "600" }}
            >
              {alarm.name}
            </Text>
            <Text style={{ color: "#f43f5e", fontSize: 20, fontWeight: "bold" }}>
              {alarm.trigger_time}
            </Text>
          </View>
          {alarm.message ? (
            <Text style={{ color: "#9ca3af", marginTop: 8 }}>
              {alarm.message}
            </Text>
          ) : null}
          <View
            style={{ flexDirection: "row", gap: 8, marginTop: 12, alignItems: "center" }}
          >
            <View
              style={{
                backgroundColor:
                  alarm.status === "active" ? "#14532d" : "#1f2937",
                borderRadius: 8,
                paddingHorizontal: 12,
                paddingVertical: 6,
              }}
            >
              <Text
                style={{
                  color: alarm.status === "active" ? "#86efac" : "#6b7280",
                  fontSize: 12,
                }}
              >
                {alarm.status}
              </Text>
            </View>
            <TouchableOpacity
              onPress={() => deleteAlarm(alarm)}
              style={{
                backgroundColor: "#450a0a",
                borderRadius: 8,
                paddingHorizontal: 12,
                paddingVertical: 6,
              }}
            >
              <Text style={{ color: "#fca5a5", fontSize: 12 }}>Delete</Text>
            </TouchableOpacity>
          </View>
        </View>
      ))}

      {alarms.length === 0 && (
        <Text style={{ color: "#4b5563" }}>
          No alarms. Create one from the web dashboard.
        </Text>
      )}
    </ScrollView>
  );
}
