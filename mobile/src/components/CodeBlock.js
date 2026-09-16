/**
 * Grok-Inspired 1-Tap Copy Code Block
 * Features tactile haptics, spring animation, and syntax styling
 */

import React, { useState, useRef } from "react";
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Animated } from "react-native";
import * as Clipboard from "expo-clipboard";
import * as Haptics from "expo-haptics";
import { Ionicons } from "@expo/vector-icons";
import { Colors } from "../theme/colors";

export const CodeBlock = ({ language = "code", code = "" }) => {
  const [copied, setCopied] = useState(false);
  const scaleAnim = useRef(new Animated.Value(1)).current;

  const handleCopy = async () => {
    try {
      await Clipboard.setStringAsync(code);
      try {
        await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      } catch (e) {
        // Haptics fallback
      }

      setCopied(true);

      // Bounce scale animation
      Animated.sequence([
        Animated.timing(scaleAnim, { toValue: 1.2, duration: 120, useNativeDriver: true }),
        Animated.spring(scaleAnim, { toValue: 1, friction: 3, useNativeDriver: true })
      ]).start();

      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.warn("Failed to copy:", err);
    }
  };

  return (
    <View style={styles.container}>
      {/* Code Block Header */}
      <View style={styles.header}>
        <View style={styles.langContainer}>
          <View style={styles.dot} />
          <Text style={styles.langText}>{language.toLowerCase()}</Text>
        </View>

        <TouchableOpacity activeOpacity={0.7} onPress={handleCopy} style={styles.copyBtn}>
          <Animated.View style={[styles.copyRow, { transform: [{ scale: scaleAnim }] }]}>
            <Ionicons
              name={copied ? "checkmark-sharp" : "copy-outline"}
              size={13}
              color={copied ? Colors.emerald : Colors.textSecondary}
            />
            <Text style={[styles.copyText, copied && styles.copiedText]}>
              {copied ? "Copied!" : "Copy code"}
            </Text>
          </Animated.View>
        </TouchableOpacity>
      </View>

      {/* Code Body */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.scrollBody}>
        <Text style={styles.codeText}>{code.trimEnd()}</Text>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 10,
    borderRadius: 12,
    backgroundColor: Colors.codeBlockBody,
    borderWidth: 1,
    borderColor: "rgba(255, 255, 255, 0.08)",
    overflow: "hidden"
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    backgroundColor: Colors.codeBlockHeader,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: "rgba(255, 255, 255, 0.05)"
  },
  langContainer: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: Colors.cyan
  },
  langText: {
    fontSize: 12,
    fontWeight: "600",
    color: Colors.textSecondary,
    fontFamily: "monospace"
  },
  copyBtn: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    backgroundColor: "rgba(255, 255, 255, 0.04)"
  },
  copyRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 5
  },
  copyText: {
    fontSize: 11,
    fontWeight: "500",
    color: Colors.textSecondary
  },
  copiedText: {
    color: Colors.emerald,
    fontWeight: "700"
  },
  scrollBody: {
    padding: 14
  },
  codeText: {
    fontSize: 13,
    lineHeight: 20,
    color: "#f3f4f6",
    fontFamily: "monospace"
  }
});
