"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Alarm } from "@/types";

export default function AlarmsPage() {
  const [alarms, setAlarms] = useState<Alarm[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", trigger_time: "07:00", message: "" });

  const load = async () => {
    setLoading(true);
    try {
      setAlarms(await api.alarms.list());
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
    await api.alarms.create(form);
    setForm({ name: "", trigger_time: "07:00", message: "" });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    await api.alarms.delete(id);
    load();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Alarms</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="rounded-lg bg-rose-600 px-4 py-2 text-sm font-medium hover:bg-rose-700"
        >
          {showForm ? "Cancel" : "Add Alarm"}
        </button>
      </div>

      {showForm && (
        <form
          onSubmit={handleCreate}
          className="space-y-4 rounded-lg border border-gray-800 bg-gray-900 p-6"
        >
          <input
            type="text"
            placeholder="Alarm name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
            className="w-full rounded-md border border-gray-700 bg-gray-800 px-3 py-2 focus:border-rose-500 focus:outline-none"
          />
          <input
            type="time"
            value={form.trigger_time}
            onChange={(e) => setForm({ ...form, trigger_time: e.target.value })}
            required
            className="rounded-md border border-gray-700 bg-gray-800 px-3 py-2 focus:border-rose-500 focus:outline-none"
          />
          <textarea
            placeholder="Message (shown on e-paper)"
            value={form.message}
            onChange={(e) => setForm({ ...form, message: e.target.value })}
            rows={2}
            className="w-full rounded-md border border-gray-700 bg-gray-800 px-3 py-2 focus:border-rose-500 focus:outline-none"
          />
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
      ) : alarms.length === 0 ? (
        <p className="text-gray-500">No alarms yet.</p>
      ) : (
        <div className="space-y-3">
          {alarms.map((alarm) => (
            <div
              key={alarm.id}
              className="flex items-center justify-between rounded-lg border border-gray-800 bg-gray-900 p-4"
            >
              <div>
                <p className="font-medium">{alarm.name}</p>
                <p className="text-sm text-gray-400">
                  {alarm.trigger_time} &middot; {alarm.status}
                  {alarm.message && ` &middot; "${alarm.message}"`}
                </p>
              </div>
              <button
                onClick={() => handleDelete(alarm.id)}
                className="rounded-md bg-red-900 px-3 py-1 text-xs text-red-300 hover:bg-red-800"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
