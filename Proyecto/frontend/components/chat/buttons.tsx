"use client";

import { toast } from "react-toastify";

export const ButtonSendSheet = ({
  email,
  name,
}: {
  email?: string | null;
  name?: string | null;
}) => {
  const onHandleSendSheet = async () => {
    if (!email) return;

    try {
      const resp = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/ai/get_excel/?user_email=${email}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        },
      );

      if (!resp.ok) {
        toast.error("Something went wrong. Please try again.");
        return;
      }

      const blob = await resp.blob();

      const url = window.URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = url;

      const currentDate = new Date();

      const formattedDate = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, "0")}-${String(
        currentDate.getDate(),
      ).padStart(2, "0")}`;

      const formattedTime = `${String(currentDate.getHours()).padStart(2, "0")}-${String(
        currentDate.getMinutes(),
      ).padStart(2, "0")}-${String(currentDate.getSeconds()).padStart(2, "0")}`;

      link.download = `${name?.replaceAll(" ", "_")}-${formattedDate}_${formattedTime}.xlsx`;

      link.click();

      window.URL.revokeObjectURL(url);
      toast.success("Sheet downloaded successfully.");
    } catch {
      toast.error("Something went wrong. Please try again.");
    }
  };

  return (
    <button
      onClick={onHandleSendSheet}
      className="w-11/12 block text-center py-2 rounded-md font-semibold border border-indigo-800/80 bg-indigo-800/80 hover:border-white hover:bg-transparent text-white transition"
    >
      Download Sheet 🗂️
    </button>
  );
};
