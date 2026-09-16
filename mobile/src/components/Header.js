/**
 * Grok Cosmic Header
 * Displays model switcher pill, Grok Mode toggle, and new chat action
 */

import React from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import * as Haptics from "expo-haptics";
import { Colors } from "../theme/colors";

export const Header = ({
  model = "prime",
  mode = "regular",
  onToggleMode,
  onNewChat,
  onOpenSettings
}) => {
  const isFunMode = mode === "fun";

  const handleToggle = () => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch (e) {}
    if (onToggleMode) onToggleMode(isFunMode ? "regular" : "fun");
  };

  return (
    <View style={styles.headerContainer}>
      {/* Left: Model Pill */}
      <TouchableOpacity activeOpacity={0.7} onPress={onOpenSettings} style={styles.modelPill}>
        <View style={styles.statusDot} />
        <Text style={styles.modelTitle}>
          {model === "prime" ? "Zieork Prime" : "Zieork Micro"}
        </Text>
        <Ionicons name="chevron-down" size={12} color={Colors.textMuted} />
      </TouchableOpacity>

      {/* Center: Grok Mode Toggle Pill */}
      <TouchableOpacity activeOpacity={0.8} onPress={handleToggle} style={styles.modeToggleOuter}>
        {isFunMode ? (
          <LinearGradient
            colors={Colors.gradients.funMode}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={styles.modeToggleGradient}
          >
            <Text style={styles.modeTextActive}>🔥 Fun</Text>
          </LinearGradient>
        ) : (
          <View style={styles.modeToggleRegular}>
            <Text style={styles.modeTextRegular}>Normal</Text>
          </View>
        )}
      </TouchableOpacity>

      {/* Right: New Chat Action */}
      <TouchableOpacity activeOpacity={0.7} onPress={onNewChat} style={styles.iconBtn}>
        <Ionicons name="create-outline" size={21} color={Colors.textPrimary} />
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  headerContainer: {
    height: 52,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 16,
    backgroundColor: Colors.background,
    borderBottomWidth: 1,
    borderBottomColor: Colors.borderSubtle
  },
  modelPill: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: Colors.surfaceCard,
    borderWidth: 1,
    borderColor: Colors.borderSubtle
  },
  statusDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: Colors.emerald
  },
  modelTitle: {
    fontSize: 13,
    fontWeight: "600",
    color: Colors.textPrimary
  },
  modeToggleOuter: {
    borderRadius: 20,
    overflow: "hidden"
  },
  modeToggleRegular: {
    paddingHorizontal: 14,
    paddingVertical: 5,
    backgroundColor: Colors.surfaceCard,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: Colors.borderSubtle
  },
  modeToggleGradient: {
    paddingHorizontal: 14,
    paddingVertical: 5,
    borderRadius: 20
  },
  modeTextRegular: {
    fontSize: 12,
    fontWeight: "500",
    color: Colors.textSecondary
  },
  modeTextActive: {
    fontSize: 12,
    fontWeight: "700",
    color: "#ffffff"
  },
  iconBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: Colors.surfaceCard
  }
});
