/**
 * Grok Main Chat Screen
 * Zieork Mobile by Mohit Dwivedi
 */

import React, { useState, useRef, useEffect } from "react";
import {
  View,
  FlatList,
  Text,
  StyleSheet,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  SafeAreaView
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import * as Haptics from "expo-haptics";
import { Colors } from "../theme/colors";
import { Header } from "../components/Header";
import { MessageItem } from "../components/MessageItem";
import { FloatingInput } from "../components/FloatingInput";
import { sendChatMessage, saveSessionToStorage } from "../services/api";

export const ChatScreen = ({ onNavigateSettings }) => {
  const [messages, setMessages] = useState([]);
  const [mode, setMode] = useState("regular"); // "regular" | "fun"
  const [model, setModel] = useState("prime"); // "prime" | "micro"
  const [isGenerating, setIsGenerating] = useState(false);
  const [sessionId, setSessionId] = useState(Date.now().toString());

  const flatListRef = useRef(null);

  const quickPrompts = [
    { id: "1", title: "Python Palindrome", desc: "Two-pointer O(1) space logic", prompt: "Write a clean Python function to check if a string is a palindrome." },
    { id: "2", title: "Explain Recursion", desc: "Simple beginner analogy", prompt: "Explain how recursion works with a simple real-world example." },
    { id: "3", title: "Who is Mohit Dwivedi?", desc: "Creator background & apps", prompt: "Who created you and what are his major software projects?" },
    { id: "4", title: "Async vs Sync", desc: "Python event loop guide", prompt: "What is the difference between synchronous and asynchronous programming in Python?" }
  ];

  const scrollToBottom = () => {
    setTimeout(() => {
      if (flatListRef.current) {
        flatListRef.current.scrollToEnd({ animated: true });
      }
    }, 100);
  };

  const handleSend = async (text) => {
    if (!text || isGenerating) return;

    const userMsg = { role: "user", content: text };
    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);
    setIsGenerating(true);
    scrollToBottom();

    // Placeholder assistant message
    const assistantPlaceholder = {
      role: "assistant",
      content: "Thinking...",
      meta: "Generating..."
    };
    setMessages([...updatedMessages, assistantPlaceholder]);

    const startTime = Date.now();

    try {
      await sendChatMessage({
        messages: updatedMessages,
        mode: mode,
        model: model,
        onComplete: (replyText, elapsedSec) => {
          const finalAssistantMsg = {
            role: "assistant",
            content: replyText,
            meta: `⏱️ ${elapsedSec}s • ${mode === "fun" ? "🔥 Fun" : "Prime"}`
          };
          const allMsgs = [...updatedMessages, finalAssistantMsg];
          setMessages(allMsgs);
          setIsGenerating(false);
          saveSessionToStorage({
            id: sessionId,
            title: text.slice(0, 30),
            messages: allMsgs,
            timestamp: Date.now()
          });
          scrollToBottom();
        },
        onError: (err) => {
          const errorMsg = {
            role: "assistant",
            content: `⚠️ Error connecting to Zieork: ${err.message}\nMake sure your server is running on the LAN URL set in the Engine tab.`,
            meta: "Failed"
          };
          setMessages([...updatedMessages, errorMsg]);
          setIsGenerating(false);
        }
      });
    } catch (e) {
      setIsGenerating(false);
    }
  };

  const handleNewChat = () => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    } catch (e) {}
    setMessages([]);
    setSessionId(Date.now().toString());
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <Header
        model={model}
        mode={mode}
        onToggleMode={setMode}
        onNewChat={handleNewChat}
        onOpenSettings={onNavigateSettings}
      />

      <KeyboardAvoidingView
        style={styles.keyboardContainer}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        keyboardVerticalOffset={Platform.OS === "ios" ? 10 : 0}
      >
        {messages.length === 0 ? (
          <View style={styles.welcomeContainer}>
            {/* Cosmic Logo */}
            <View style={styles.logoWrapper}>
              <LinearGradient
                colors={mode === "fun" ? Colors.gradients.funMode : Colors.gradients.cosmicGlow}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
                style={styles.logoGradient}
              >
                <Ionicons name="flash-sharp" size={36} color="#ffffff" />
              </LinearGradient>
            </View>

            <Text style={styles.welcomeTitle}>
              {mode === "fun" ? "Grok Mode Activated" : "What can I solve?"}
            </Text>
            <Text style={styles.welcomeSubtitle}>
              Sovereign Local Intelligence by{" "}
              <Text style={{ color: Colors.cyan, fontWeight: "600" }}>Mohit Dwivedi</Text>
            </Text>

            {/* Quick Prompt Cards */}
            <View style={styles.chipsGrid}>
              {quickPrompts.map((item) => (
                <TouchableOpacity
                  key={item.id}
                  activeOpacity={0.7}
                  onPress={() => handleSend(item.prompt)}
                  style={styles.chipCard}
                >
                  <Text style={styles.chipTitle}>{item.title}</Text>
                  <Text style={styles.chipDesc}>{item.desc}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        ) : (
          <FlatList
            ref={flatListRef}
            data={messages}
            keyExtractor={(_, index) => `msg-${index}`}
            renderItem={({ item }) => <MessageItem message={item} />}
            contentContainerStyle={styles.listContent}
            onContentSizeChange={scrollToBottom}
          />
        )}

        <FloatingInput
          onSend={handleSend}
          isGenerating={isGenerating}
          mode={mode}
        />
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: Colors.background
  },
  keyboardContainer: {
    flex: 1
  },
  welcomeContainer: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 20
  },
  logoWrapper: {
    width: 68,
    height: 68,
    borderRadius: 34,
    overflow: "hidden",
    marginBottom: 16
  },
  logoGradient: {
    width: "100%",
    height: "100%",
    alignItems: "center",
    justifyContent: "center"
  },
  welcomeTitle: {
    fontSize: 22,
    fontWeight: "700",
    color: Colors.textPrimary,
    marginBottom: 6
  },
  welcomeSubtitle: {
    fontSize: 13,
    color: Colors.textMuted,
    marginBottom: 28
  },
  chipsGrid: {
    width: "100%",
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
    justifyContent: "space-between"
  },
  chipCard: {
    width: "48%",
    backgroundColor: Colors.surfaceCard,
    borderRadius: 14,
    padding: 12,
    borderWidth: 1,
    borderColor: Colors.borderSubtle
  },
  chipTitle: {
    fontSize: 13,
    fontWeight: "600",
    color: Colors.textPrimary,
    marginBottom: 4
  },
  chipDesc: {
    fontSize: 11,
    color: Colors.textMuted
  },
  listContent: {
    paddingVertical: 12
  }
});
