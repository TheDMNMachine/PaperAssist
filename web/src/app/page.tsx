import { api } from "@/lib/api";
import type { Screen, Alarm } from "@/types";

async function getData() {
  try {
    const [screens, alarms] = await Promise.all([
      api.screens.list(),
      api.alarms.getActive(),
    ]);
    return { screens, alarms, error: null };
  } catch {
    return { screens: [] as Screen[], alarms: [] as Alarm[], error: "Failed to fetch data" };
  }
}

export const dynamic = "force-dynamic";

export default async function Dashboard() {
  const { screens, alarms, error } = await getData();
  const currentScreen = screens.find((s) => s.is_active);

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold">Dashboard</h1>

      {error && (
        <div className="rounded-lg border border-red-800 bg-red-950 p-4 text-red-300">
          {error}
        </div>
      )}

      <section className="rounded-lg border border-gray-800 bg-gray-900 p-6">
        <h2 className="mb-4 text-lg font-semibold text-gray-300">
          Current Screen
        </h2>
        {currentScreen ? (
          <div className="space-y-2">
            <p className="text-xl font-medium">{currentScreen.title}</p>
            <p className="text-gray-400">{currentScreen.content}</p>
            <span className="inline-block rounded-full bg-gray-800 px-3 py-1 text-xs text-gray-400">
              {currentScreen.screen_type}
            </span>
          </div>
        ) : (
          <p className="text-gray-500">No active screen</p>
        )}
      </section>

      <div className="grid gap-6 md:grid-cols-2">
        <section className="rounded-lg border border-gray-800 bg-gray-900 p-6">
          <h2 className="mb-4 text-lg font-semibold text-gray-300">
            Screens ({screens.length})
          </h2>
          {screens.length > 0 ? (
            <ul className="space-y-2">
              {screens.map((screen) => (
                <li
                  key={screen.id}
                  className="flex items-center justify-between rounded-md bg-gray-800 px-3 py-2"
                >
                  <span>{screen.title}</span>
                  <span
                    className={`h-2 w-2 rounded-full ${screen.is_active ? "bg-green-500" : "bg-gray-600"}`}
                  />
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500">No screens configured</p>
          )}
        </section>

        <section className="rounded-lg border border-gray-800 bg-gray-900 p-6">
          <h2 className="mb-4 text-lg font-semibold text-gray-300">
            Active Alarms ({alarms.length})
          </h2>
          {alarms.length > 0 ? (
            <ul className="space-y-2">
              {alarms.map((alarm) => (
                <li
                  key={alarm.id}
                  className="flex items-center justify-between rounded-md bg-gray-800 px-3 py-2"
                >
                  <span>{alarm.name}</span>
                  <span className="text-sm text-gray-400">
                    {alarm.trigger_time}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500">No active alarms</p>
          )}
        </section>
      </div>
    </div>
  );
}
