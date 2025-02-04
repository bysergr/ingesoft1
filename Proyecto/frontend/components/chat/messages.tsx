import { useEffect, useState } from "react";
import { marked } from "marked";

export function UserMessage({
  message,
  name,
}: {
  message: string;
  name?: string;
}) {
  return (
    <li className="flex justify-end">
      <div className="w-fit lg:max-w-[80%] bg-white py-2 px-4 border-neutral-200 border rounded-2xl">
        <label className="font-semibold tracking-wider text-[10px]">
          {name || "User"}
        </label>
        <p className="text-wrap break-words text-sm">{message}</p>
      </div>
    </li>
  );
}

export function BotMessage({ message }: { message: string }) {
  return (
    <div className="w-fit lg:max-w-[80%]">
      <div className="bg-white py-2 px-4 border-neutral-200 border rounded-2xl">
        <label className="font-semibold tracking-wider text-[10px]">
          NaurBotMX
        </label>
        <div
          className="text-wrap break-words markdown"
          dangerouslySetInnerHTML={{ __html: marked(message) }}
        ></div>
      </div>
    </div>
  );
}

export function LoadingMessage() {
  const [message, setMessage] = useState("...");

  useEffect(() => {
    const interval = setInterval(() => {
      setMessage((prev) => {
        if (prev === ".") {
          return "..";
        } else if (prev === "..") {
          return "...";
        } else {
          return ".";
        }
      });
    }, 500);
    return () => clearInterval(interval);
  }, []);

  return (
    <li>
      <div className="w-fit bg-white py-2 px-4 border-neutral-200 border rounded-2xl">
        <p className="w-[11px]">{message}</p>
      </div>
    </li>
  );
}
