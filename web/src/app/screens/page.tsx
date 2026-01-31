"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Screen, ScreenType } from "@/types";

export default function ScreensPage() {
  const [screens, setScreens] = useState<Screen[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    title: "",
    content: "",
    screen_type: "text" as ScreenType,
  });

  const load = async () => {
    setLoading(true);
    try {
      setScreens(await api.screens.list());
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.screens.create(form);
    setForm({ title: "", content: "", screen_type: "text" });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    await api.screens.delete(id);
    load();
  };

  const handleToggle = async (screen: Screen) => {
    await api.screens.update(screen.id, { is_active: !screen.is_active });
    load();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Screens</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="rounded-lg bg-rose-600 px-4 py-2 text-sm font-medium hover:bg-rose-700"
        >
          {showForm ? "Cancel" : "Add Screen"}
        </button>
      </div>

      {showForm && (
        <form
          onSubmit={handleCreate}
          className="space-y-4 rounded-lg border border-gray-800 bg-gray-900 p-6"
        >
          <input
            type="text"
            placeholder="Title"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            required
            className="w-full rounded-md border border-gray-700 bg-gray-800 px-3 py-2 focus:border-rose-500 focus:outline-none"
          />
          <textarea
            placeholder="Content"
            value={form.content}
            onChange={(e) => setForm({ ...form, content: e.target.value })}
            rows={3}
            className="w-full rounded-md border border-gray-700 bg-gray-800 px-3 py-2 focus:border-rose-500 focus:outline-none"
          />
          <select
            value={form.screen_type}
            onChange={(e) =>
              setForm({ ...form, screen_type: e.target.value as ScreenType })
            }
            className="rounded-md border border-gray-700 bg-gray-800 px-3 py-2"
          >
            <option value="text">Text</option>
            <option value="weather">Weather</option>
            <option value="calendar">Calendar</option>
            <option value="custom">Custom</option>
          </select>
          <button
            type="submit"
            className="rounded-lg bg-rose-600 px-4 py-2 text-sm font-medium hover:bg-rose-700"
          >
            Create
          </button>
        </form>
      )}

      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : screens.length === 0 ? (
        <p className="text-gray-500">No screens yet. Create one above.</p>
      ) : (
        <div className="space-y-3">
          {screens.map((screen) => (
            <div
              key={screen.id}
              className="flex items-center justify-between rounded-lg border border-gray-800 bg-gray-900 p-4"
            >
              <div>
                <p className="font-medium">{screen.title}</p>
                <p className="text-sm text-gray-400">
                  {screen.screen_type} &middot; order: {screen.display_order}
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleToggle(screen)}
                  className={`rounded-md px-3 py-1 text-xs ${
                    screen.is_active
                      ? "bg-green-900 text-green-300"
                      : "bg-gray-800 text-gray-500"
                  }`}
                >
                  {screen.is_active ? "Active" : "Inactive"}
                </button>
                <button
                  onClick={() => handleDelete(screen.id)}
                  className="rounded-md bg-red-900 px-3 py-1 text-xs text-red-300 hover:bg-red-800"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
