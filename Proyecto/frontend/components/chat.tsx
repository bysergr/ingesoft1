"use client";

import { useEffect, useRef, useState } from "react";
import { HiOutlineArrowSmUp } from "react-icons/hi";
import { toast } from "react-toastify";
import clsx from "clsx";

import {
  BotMessage,
  LoadingMessage,
  UserMessage,
} from "@/components/chat/messages";
import { getRandomNumberInRange } from "@/lib/random";
import { NomsMessage } from "@/components/chat/noms";

type Message = {
  owner: "bot" | "user";
  message: string;
  noms?: string[];
  lang?: "es" | "en";
};

interface MessageBackend {
  owner: "ai" | "human";
  message: string;
  noms?: string[];
  lang?: "es" | "en";
}

export const Chat = ({ email, name }: { email?: string; name?: string }) => {
  const [userID, setUserID] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [textAreaMessage, setTextAreaMessage] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [rows, setRows] = useState(1);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const addMessage = (
    owner: "user" | "bot",
    message: string,
    noms: string[] = [],
    lang: "es" | "en",
  ) => {
    setMessages((prev) => [
      ...prev,
      {
        owner,
        message,
        noms,
        lang,
      },
    ]);
  };

  useEffect(() => {
    if (!email) {
      setUserID(getRandomNumberInRange(10 ** 6, 10 ** 7).toString());
    }

    setMessages([
      {
        owner: "bot",
        message:
          "Hello! I'm your Import Bot, ready to assist you in determining tariffs, taxes, and necessary certifications for your imports. Just provide the product you want to import, its country of origin, and an estimated value. No worries if you’re missing some details—we’ll make the most of the information you have!",
      },
    ]);

    if (email) {
      fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/ai/bot_conversation/${email}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        },
      )
        .then((response) => response.json())
        .then((data) => {
          data.conversation.forEach((message: MessageBackend) => {
            if (message.owner === "human") {
              addMessage(
                "user",
                message.message,
                message.noms,
                message.lang || "en",
              );
            }

            if (message.owner === "ai") {
              addMessage(
                "bot",
                message.message,
                message.noms,
                message.lang || "en",
              );
            }
          });
        })
        .catch(() => {
          setMessages((prev) => [
            ...prev,
            {
              owner: "bot",
              message:
                "Sorry, I couldn't retrieve your previous messages. 😔 Please try again later.",
            },
          ]);
          toast.error("Something went wrong. Please try again.");
        });
    }

    return () => {
      setMessages([]);
    };
  }, [email]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollTop = messagesEndRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const handleMessage = async (message: string) => {
    setLoading(true);

    try {
      const body: Partial<{
        prompt: string;
        user_email: string;
        user_id: string;
      }> = {
        prompt: message,
      };

      if (email) {
        body.user_email = email;
      } else {
        body.user_id = userID as string;
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/ai/importation/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(body),
        },
      );

      if (!response.ok) {
        throw new Error("Request failed.");
      }

      const data = await response.json();

      if (!data.message) {
        throw new Error("Response not found.");
      }

      setMessages((prev) => [
        ...prev,
        {
          owner: "bot",
          message: data.message,
          noms: data.noms,
          lang: data.lang,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          owner: "bot",
          message: "Sorry, I couldn't process your request. 😔",
        },
      ]);
      toast.error("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleInput = (e: React.FormEvent<HTMLTextAreaElement>) => {
    const textarea = e.currentTarget;
    textarea.style.height = "auto";
    textarea.style.height = `${textarea.scrollHeight}px`;

    setTextAreaMessage(textarea.value);
    setRows(textarea.value.split("\n").length);
  };

  const handleKeyPress = async (
    e: React.KeyboardEvent<HTMLTextAreaElement>,
  ) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();

      const message = e.currentTarget.value;

      setTextAreaMessage("");
      setRows(1);

      if (message.trim().replace(/\n/g, "").length === 0) return;

      setMessages((prev) => [...prev, { owner: "user", message: message }]);
      await handleMessage(message);
    }
  };

  const handleOnClick = async () => {
    if (!textAreaMessage) return;

    const message = textAreaMessage;

    setTextAreaMessage("");
    setRows(1);

    if (message.trim().replace(/\n/g, "").length === 0) return;

    setMessages((prev) => [...prev, { owner: "user", message: message }]);
    await handleMessage(message);
  };

  return (
    <div className="h-[calc(100vh-77px)] m-0 p-0 flex flex-col justify-between items-center gap-y-4">
      <div className="overflow-y-scroll w-full h-full" ref={messagesEndRef}>
        <ul className="sm:w-[calc(80%+22px)] lg:w-[calc(70%+22px)] flex flex-col gap-y-2 mx-4 sm:mx-auto mt-8">
          {messages.map((message, index) => {
            if (message.owner === "user") {
              return (
                <UserMessage
                  key={index}
                  name={name}
                  message={message.message}
                />
              );
            } else {
              return (
                <li key={index}>
                  <BotMessage message={message.message} />
                  {message.noms &&
                    [...new Set(message.noms)].map((nom: string) => (
                      <NomsMessage
                        key={nom + index}
                        nom={nom}
                        lang={message.lang || "en"}
                      />
                    ))}
                </li>
              );
            }
          })}
          {loading && <LoadingMessage />}
        </ul>
      </div>
      <div className="flex w-full gap-2 justify-center items-center">
        <textarea
          value={textAreaMessage}
          className={clsx(
            rows > 5 ? "overflow-y-auto" : "overflow-y-hidden",
            "resize-none max-h-52 border border-neutral-200 py-2 px-4 rounded-2xl mx-4 w-full sm:w-[70%] lg:w-1/2",
          )}
          rows={1}
          disabled={loading}
          placeholder="Write a message..."
          onInput={handleInput}
          onKeyDown={handleKeyPress}
        />
        <button
          disabled={loading}
          className="md:hidden p-2 bg-neutral-200 rounded-full mr-4"
          onClick={handleOnClick}
        >
          <HiOutlineArrowSmUp />
        </button>
      </div>
    </div>
  );
};
