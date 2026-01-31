import { useEffect, useState } from "react";
import { View, Text, ScrollView, RefreshControl } from "react-native";
import { api } from "@/lib/api";
import type { Screen, Alarm } from "@/types";

export default function Dashboard() {
  const [screens, setScreens] = useState<Screen[]>([]);
  const [alarms, setAlarms] = useState<Alarm[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const load = async () => {
    try {
      const [s, a] = await Promise.all([
        api.screens.list(),
        api.alarms.getActive(),
      ]);
      setScreens(s);
      setAlarms(a);
    } catch (e) {
      console.error(e);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  useEffect(() => {
    load();
  }, []);

  const current = screens.find((s) => s.is_active);

  return (
    <ScrollView
      style={{ flex: 1, backgroundColor: "#030712" }}
      contentContainerStyle={{ padding: 16, gap: 16 }}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <Text style={{ color: "#f9fafb", fontSize: 24, fontWeight: "bold" }}>
        Dashboard
      </Text>

      <View
        style={{
          backgroundColor: "#111827",
          borderRadius: 12,
          padding: 16,
          borderWidth: 1,
          borderColor: "#1f2937",
        }}
      >
        <Text style={{ color: "#9ca3af", marginBottom: 8 }}>
          Current Screen
        </Text>
        {current ? (
          <>
            <Text style={{ color: "#f9fafb", fontSize: 18, fontWeight: "600" }}>
              {current.title}
            </Text>
            <Text style={{ color: "#6b7280", marginTop: 4 }}>
              {current.content}
            </Text>
          </>
        ) : (
          <Text style={{ color: "#4b5563" }}>No active screen</Text>
        )}
      </View>

      <View
        style={{
          backgroundColor: "#111827",
          borderRadius: 12,
          padding: 16,
          borderWidth: 1,
          borderColor: "#1f2937",
        }}
      >
        <Text style={{ color: "#9ca3af", marginBottom: 8 }}>
          Screens ({screens.length})
        </Text>
        {screens.map((s) => (
          <View
            key={s.id}
            style={{
              flexDirection: "row",
              justifyContent: "space-between",
              alignItems: "center",
              backgroundColor: "#1f2937",
              borderRadius: 8,
              padding: 12,
              marginBottom: 8,
            }}
          >
            <Text style={{ color: "#f9fafb" }}>{s.title}</Text>
            <View
              style={{
                width: 8,
                height: 8,
                borderRadius: 4,
                backgroundColor: s.is_active ? "#22c55e" : "#4b5563",
              }}
            />
          </View>
        ))}
      </View>

      <View
        style={{
          backgroundColor: "#111827",
          borderRadius: 12,
          padding: 16,
          borderWidth: 1,
          borderColor: "#1f2937",
        }}
      >
        <Text style={{ color: "#9ca3af", marginBottom: 8 }}>
          Active Alarms ({alarms.length})
        </Text>
        {alarms.map((a) => (
          <View
            key={a.id}
            style={{
              flexDirection: "row",
              justifyContent: "space-between",
              backgroundColor: "#1f2937",
              borderRadius: 8,
              padding: 12,
              marginBottom: 8,
            }}
          >
            <Text style={{ color: "#f9fafb" }}>{a.name}</Text>
            <Text style={{ color: "#6b7280" }}>{a.trigger_time}</Text>
          </View>
        ))}
        {alarms.length === 0 && (
          <Text style={{ color: "#4b5563" }}>No active alarms</Text>
        )}
      </View>
    </ScrollView>
  );
}
