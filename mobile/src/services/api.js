/**
 * Zieork Mobile API Service
 * Handles communication with Zieork Prime (1.23B) and Zieork Micro
 */

import AsyncStorage from "@react-native-async-storage/async-storage";

const DEFAULT_SERVER_URL = "http://localhost:5000";
const STORAGE_SERVER_KEY = "@zieork_server_url";
const STORAGE_SESSIONS_KEY = "@zieork_mobile_sessions";

export const getStoredServerUrl = async () => {
  try {
    const url = await AsyncStorage.getItem(STORAGE_SERVER_KEY);
    return url || DEFAULT_SERVER_URL;
  } catch (e) {
    return DEFAULT_SERVER_URL;
  }
};

export const setStoredServerUrl = async (url) => {
  try {
    const cleaned = url.trim().replace(/\/+$/, "");
    await AsyncStorage.setItem(STORAGE_SERVER_KEY, cleaned);
    return cleaned;
  } catch (e) {
    return url;
  }
};

export const getStoredSessions = async () => {
  try {
    const data = await AsyncStorage.getItem(STORAGE_SESSIONS_KEY);
    return data ? JSON.parse(data) : [];
  } catch (e) {
    return [];
  }
};

export const saveSessionToStorage = async (session) => {
  try {
    const sessions = await getStoredSessions();
    const idx = sessions.findIndex((s) => s.id === session.id);
    if (idx >= 0) {
      sessions[idx] = session;
    } else {
      sessions.unshift(session);
    }
    await AsyncStorage.setItem(STORAGE_SESSIONS_KEY, JSON.stringify(sessions.slice(0, 30)));
  } catch (e) {
    console.warn("Failed to save session:", e);
  }
};

export const sendChatMessage = async ({
  messages,
  mode = "regular", // "regular" | "fun"
  model = "prime",
  onChunk,
  onComplete,
  onError
}) => {
  const serverUrl = await getStoredServerUrl();
  const endpoint = `${serverUrl}/v1/chat/completions`;

  // Customize persona based on Grok mode
  let modePrompt = "";
  if (mode === "fun") {
    modePrompt =
      "Mode: Fun Mode (Grok Style).\n" +
      "You are witty, sharp, humorous, and delightfully rebellious with a cosmic sci-fi personality, " +
      "while retaining deep technical accuracy and never compromising on code quality. " +
      "You were created and developed by Mohit Dwivedi.";
  }

  const payloadMessages = modePrompt
    ? [{ role: "system", content: modePrompt }, ...messages]
    : messages;

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: model === "prime" ? "zieork-prime-1b" : "zieork-micro",
        preset: mode === "fun" ? "creative" : "chatgpt",
        stream: false,
        messages: payloadMessages
      })
    });

    if (!response.ok) {
      // Try fallback to /api/chat
      const fallbackRes = await fetch(`${serverUrl}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: messages[messages.length - 1].content,
          model: model,
          messages: messages
        })
      });
      if (!fallbackRes.ok) {
        throw new Error(`Server status: ${response.status}`);
      }
      const fbData = await fallbackRes.json();
      const content = fbData.response || "No response received.";
      if (onComplete) onComplete(content, fbData.elapsed_seconds || 1.2);
      return content;
    }

    const data = await response.json();
    const content = data.choices?.[0]?.message?.content || "";
    if (onComplete) onComplete(content, 1.4);
    return content;
  } catch (error) {
    if (onError) onError(error);
    throw error;
  }
};
