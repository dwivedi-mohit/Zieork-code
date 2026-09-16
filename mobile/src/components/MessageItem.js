/**
 * Grok Message Item Component
 * Renders user cards and Zieork markdown responses with interactive CodeBlocks
 */

import React from "react";
import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import * as Clipboard from "expo-clipboard";
import * as Haptics from "expo-haptics";
import { LinearGradient } from "expo-linear-gradient";
import { Colors } from "../theme/colors";
import { CodeBlock } from "./CodeBlock";

export const MessageItem = ({ message, onSpeak }) => {
  const isUser = message.role === "user";

  const handleCopyFull = async () => {
    await Clipboard.setStringAsync(message.content);
    try {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch (e) {}
  };

  if (isUser) {
    return (
      <View style={styles.userRow}>
        <View style={styles.userBubble}>
          <Text style={styles.userText}>{message.content}</Text>
        </View>
      </View>
    );
  }

  // Parse markdown code blocks vs text
  const renderAssistantContent = (text) => {
    if (!text) return null;

    const parts = [];
    const codeBlockRegex = /```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g;
    let lastIndex = 0;
    let match;

    while ((match = codeBlockRegex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        parts.push({
          type: "text",
          content: text.slice(lastIndex, match.index)
        });
      }
      parts.push({
        type: "code",
        lang: match[1] || "code",
        content: match[2]
      });
      lastIndex = match.index + match[0].length;
    }

    if (lastIndex < text.length) {
      parts.push({
        type: "text",
        content: text.slice(lastIndex)
      });
    }

    return parts.map((part, idx) => {
      if (part.type === "code") {
        return (
          <CodeBlock
            key={`code-${idx}`}
            language={part.lang}
            code={part.content}
          />
        );
      }
      return (
        <Text key={`text-${idx}`} style={styles.assistantText}>
          {part.content}
        </Text>
      );
    });
  };

  return (
    <View style={styles.assistantRow}>
      {/* Grok Avatar */}
      <View style={styles.avatarContainer}>
        <LinearGradient
          colors={Colors.gradients.cosmicGlow}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={styles.avatarGradient}
        >
          <Ionicons name="flash-sharp" size={14} color="#ffffff" />
        </LinearGradient>
      </View>

      {/* Content Container */}
      <View style={styles.contentContainer}>
        {renderAssistantContent(message.content)}

        {/* Action Row */}
        <View style={styles.actionRow}>
          <TouchableOpacity
            activeOpacity={0.7}
            onPress={handleCopyFull}
            style={styles.actionBtn}
          >
            <Ionicons name="copy-outline" size={14} color={Colors.textMuted} />
          </TouchableOpacity>

          {onSpeak && (
            <TouchableOpacity
              activeOpacity={0.7}
              onPress={() => onSpeak(message.content)}
              style={styles.actionBtn}
            >
              <Ionicons name="volume-medium-outline" size={15} color={Colors.textMuted} />
            </TouchableOpacity>
          )}

          {message.meta && (
            <Text style={styles.metaStat}>{message.meta}</Text>
          )}
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  userRow: {
    flexDirection: "row",
    justifyContent: "flex-end",
    marginVertical: 6,
    paddingHorizontal: 16
  },
  userBubble: {
    backgroundColor: Colors.userBubble,
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 20,
    borderBottomRightRadius: 4,
    maxWidth: "85%",
    borderWidth: 1,
    borderColor: Colors.borderSubtle
  },
  userText: {
    fontSize: 15,
    lineHeight: 21,
    color: Colors.textPrimary
  },
  assistantRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    marginVertical: 10,
    paddingHorizontal: 16,
    gap: 12
  },
  avatarContainer: {
    width: 28,
    height: 28,
    borderRadius: 14,
    overflow: "hidden",
    marginTop: 2
  },
  avatarGradient: {
    width: "100%",
    height: "100%",
    alignItems: "center",
    justifyContent: "center"
  },
  contentContainer: {
    flex: 1
  },
  assistantText: {
    fontSize: 15,
    lineHeight: 23,
    color: Colors.textPrimary
  },
  actionRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    marginTop: 8
  },
  actionBtn: {
    padding: 4
  },
  metaStat: {
    fontSize: 11,
    color: Colors.textMuted,
    marginLeft: "auto"
  }
});
