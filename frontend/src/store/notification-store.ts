import { create } from "zustand";

type NotificationItem = {
  id: string;
  title: string;
  description?: string;
  status?: "info" | "success" | "warning" | "error";
  createdAt: string;
};

type NotificationState = {
  notifications: NotificationItem[];
  pushNotification: (notification: Omit<NotificationItem, "id" | "createdAt">) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
};

export const notificationStore = create<NotificationState>((set) => ({
  notifications: [],
  pushNotification: (notification) =>
    set((state) => ({
      notifications: [
        {
          ...notification,
          id: crypto.randomUUID(),
          createdAt: new Date().toISOString(),
        },
        ...state.notifications,
      ].slice(0, 50),
    })),
  removeNotification: (id) => set((state) => ({ notifications: state.notifications.filter((item) => item.id !== id) })),
  clearNotifications: () => set({ notifications: [] }),
}));
