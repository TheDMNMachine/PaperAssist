import { useEffect, useState } from "react";
import { View, Text, ScrollView, TouchableOpacity, Alert } from "react-native";
import { api } from "@/lib/api";
import type { Screen } from "@/types";

export default function ScreensScreen() {
  const [screens, setScreens] = useState<Screen[]>([]);

  const load = async () => {
    try {
      setScreens(await api.screens.list());
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const toggleActive = async (screen: Screen) => {
    await api.screens.update(screen.id, { is_active: !screen.is_active });
    load();
  };

  const deleteScreen = (screen: Screen) => {
    Alert.alert("Delete", `Delete "${screen.title}"?`, [
      { text: "Cancel", style: "cancel" },
      {
        text: "Delete",
        style: "destructive",
        onPress: async () => {
          await api.screens.delete(screen.id);
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
        Screens
      </Text>

      {screens.map((screen) => (
        <View
          key={screen.id}
          style={{
            backgroundColor: "#111827",
            borderRadius: 12,
            padding: 16,
            borderWidth: 1,
            borderColor: "#1f2937",
          }}
        >
          <Text style={{ color: "#f9fafb", fontSize: 16, fontWeight: "600" }}>
            {screen.title}
          </Text>
          <Text style={{ color: "#6b7280", marginTop: 4 }}>
            {screen.screen_type} &middot; order: {screen.display_order}
          </Text>
          {screen.content ? (
            <Text style={{ color: "#9ca3af", marginTop: 8 }}>
              {screen.content}
            </Text>
          ) : null}
          <View
            style={{
              flexDirection: "row",
              gap: 8,
              marginTop: 12,
            }}
          >
            <TouchableOpacity
              onPress={() => toggleActive(screen)}
              style={{
                backgroundColor: screen.is_active ? "#14532d" : "#1f2937",
                borderRadius: 8,
                paddingHorizontal: 12,
                paddingVertical: 6,
              }}
            >
              <Text
                style={{
                  color: screen.is_active ? "#86efac" : "#6b7280",
                  fontSize: 12,
                }}
              >
                {screen.is_active ? "Active" : "Inactive"}
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              onPress={() => deleteScreen(screen)}
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

      {screens.length === 0 && (
        <Text style={{ color: "#4b5563" }}>
          No screens. Create one from the web dashboard.
        </Text>
      )}
    </ScrollView>
  );
}
