import { Tabs } from "expo-router";
import { StatusBar } from "expo-status-bar";

export default function RootLayout() {
  return (
    <>
      <StatusBar style="light" />
      <Tabs
        screenOptions={{
          headerStyle: { backgroundColor: "#111827" },
          headerTintColor: "#f9fafb",
          tabBarStyle: { backgroundColor: "#111827", borderTopColor: "#1f2937" },
          tabBarActiveTintColor: "#f43f5e",
          tabBarInactiveTintColor: "#6b7280",
        }}
      >
        <Tabs.Screen name="index" options={{ title: "Dashboard" }} />
        <Tabs.Screen name="screens/index" options={{ title: "Screens" }} />
        <Tabs.Screen name="alarms/index" options={{ title: "Alarms" }} />
        <Tabs.Screen name="bluetooth/index" options={{ title: "Bluetooth" }} />
      </Tabs>
    </>
  );
}
