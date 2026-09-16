/**
 * Zieork Mobile — Grok-Inspired Sovereign AI App
 * Built for Expo Go / React Native
 * Created by Mohit Dwivedi (https://mohitdwivedi.in)
 */

import React, { useState } from "react";
import { View, StyleSheet } from "react-native";
import { StatusBar } from "expo-status-bar";
import { SafeAreaProvider } from "react-native-safe-area-context";

import { Colors } from "./src/theme/colors";
import { TabBar } from "./src/components/TabBar";
import { ChatScreen } from "./src/screens/ChatScreen";
import { ExploreScreen } from "./src/screens/ExploreScreen";
import { HistoryScreen } from "./src/screens/HistoryScreen";
import { SettingsScreen } from "./src/screens/SettingsScreen";

export default function App() {
  const [activeTab, setActiveTab] = useState("chat");
  const [mode, setMode] = useState("regular"); // "regular" | "fun"

  return (
    <SafeAreaProvider>
      <View style={styles.appRoot}>
        <StatusBar style="light" backgroundColor={Colors.background} />

        {/* Screen Switcher */}
        <View style={styles.screenContainer}>
          {activeTab === "chat" && (
            <ChatScreen onNavigateSettings={() => setActiveTab("settings")} />
          )}
          {activeTab === "explore" && <ExploreScreen />}
          {activeTab === "history" && (
            <HistoryScreen
              onSelectSession={(session) => {
                setActiveTab("chat");
              }}
            />
          )}
          {activeTab === "settings" && <SettingsScreen />}
        </View>

        {/* Grok Bottom Navigation Tab Bar */}
        <TabBar
          activeTab={activeTab}
          onSelectTab={setActiveTab}
          mode={mode}
        />
      </View>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  appRoot: {
    flex: 1,
    backgroundColor: Colors.background
  },
  screenContainer: {
    flex: 1
  }
});
