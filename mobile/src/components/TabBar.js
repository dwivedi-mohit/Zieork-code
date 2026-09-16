/**
 * Grok Bottom Navigation Tab Bar
 * Smooth 4-tab bar with glowing active indicator
 */

import React from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import * as Haptics from "expo-haptics";
import { Colors } from "../theme/colors";

export const TabBar = ({ activeTab = "chat", onSelectTab, mode = "regular" }) => {
  const isFunMode = mode === "fun";
  const activeColor = isFunMode ? Colors.flameOrange : Colors.cyan;

  const tabs = [
    { id: "chat", label: "Chat", icon: "chatbubble-ellipses", iconOutline: "chatbubble-ellipses-outline" },
    { id: "explore", label: "Discover", icon: "compass", iconOutline: "compass-outline" },
    { id: "history", label: "Threads", icon: "time", iconOutline: "time-outline" },
    { id: "settings", label: "Engine", icon: "hardware-chip", iconOutline: "hardware-chip-outline" }
  ];

  const handlePress = (tabId) => {
    try {
      Haptics.selectionAsync();
    } catch (e) {}
    onSelectTab(tabId);
  };

  return (
    <View style={styles.tabContainer}>
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <TouchableOpacity
            key={tab.id}
            activeOpacity={0.7}
            onPress={() => handlePress(tab.id)}
            style={styles.tabItem}
          >
            <Ionicons
              name={isActive ? tab.icon : tab.iconOutline}
              size={22}
              color={isActive ? activeColor : Colors.textMuted}
            />
            <Text style={[styles.tabLabel, isActive && { color: activeColor, fontWeight: "700" }]}>
              {tab.label}
            </Text>
            {isActive && <View style={[styles.activeDot, { backgroundColor: activeColor }]} />}
          </TouchableOpacity>
        );
      })}
    </View>
  );
};

const styles = StyleSheet.create({
  tabContainer: {
    height: 58,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-around",
    backgroundColor: Colors.surface,
    borderTopWidth: 1,
    borderTopColor: Colors.borderSubtle,
    paddingBottom: 4
  },
  tabItem: {
    alignItems: "center",
    justifyContent: "center",
    flex: 1,
    position: "relative"
  },
  tabLabel: {
    fontSize: 10.5,
    marginTop: 3,
    color: Colors.textMuted,
    fontWeight: "500"
  },
  activeDot: {
    width: 4,
    height: 4,
    borderRadius: 2,
    marginTop: 2
  }
});
