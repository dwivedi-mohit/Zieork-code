/**
 * Grok Threads / History Screen
 * Searchable thread history with instant session resume
 */

import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TextInput,
  TouchableOpacity,
  SafeAreaView
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import AsyncStorage from "@react-native-async-storage/async-storage";
import * as Haptics from "expo-haptics";
import { Colors } from "../theme/colors";
import { getStoredSessions } from "../services/api";

export const HistoryScreen = ({ onSelectSession }) => {
  const [sessions, setSessions] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");

  const loadSessions = async () => {
    const list = await getStoredSessions();
    setSessions(list);
  };

  useEffect(() => {
    loadSessions();
  }, []);

  const filteredSessions = sessions.filter((s) =>
    s.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const clearAllHistory = async () => {
    try {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
    } catch (e) {}
    await AsyncStorage.removeItem("@zieork_mobile_sessions");
    setSessions([]);
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Threads</Text>
          {sessions.length > 0 && (
            <TouchableOpacity onPress={clearAllHistory} style={styles.clearBtn}>
              <Text style={styles.clearText}>Clear All</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* Search Bar */}
        <View style={styles.searchBar}>
          <Ionicons name="search-outline" size={16} color={Colors.textMuted} />
          <TextInput
            style={styles.searchInput}
            placeholder="Search past threads..."
            placeholderTextColor={Colors.textMuted}
            value={searchQuery}
            onChangeText={setSearchQuery}
            keyboardAppearance="dark"
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity onPress={() => setSearchQuery("")}>
              <Ionicons name="close-circle" size={16} color={Colors.textMuted} />
            </TouchableOpacity>
          )}
        </View>

        {/* List */}
        {filteredSessions.length === 0 ? (
          <View style={styles.emptyView}>
            <Ionicons name="chatbubbles-outline" size={48} color={Colors.textDark} />
            <Text style={styles.emptyTitle}>No Threads Found</Text>
            <Text style={styles.emptySubtitle}>
              Conversations you start with Zieork Prime will be saved here.
            </Text>
          </View>
        ) : (
          <FlatList
            data={filteredSessions}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => (
              <TouchableOpacity
                activeOpacity={0.7}
                onPress={() => onSelectSession && onSelectSession(item)}
                style={styles.threadItem}
              >
                <View style={styles.threadIcon}>
                  <Ionicons name="chatbubble-outline" size={18} color={Colors.cyan} />
                </View>
                <View style={styles.threadDetails}>
                  <Text style={styles.threadTitle} numberOfLines={1}>
                    {item.title}
                  </Text>
                  <Text style={styles.threadDate}>
                    {new Date(item.timestamp).toLocaleDateString()} • {item.messages.length} messages
                  </Text>
                </View>
                <Ionicons name="chevron-forward" size={14} color={Colors.textMuted} />
              </TouchableOpacity>
            )}
          />
        )}
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: Colors.background
  },
  container: {
    flex: 1,
    padding: 16
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 16
  },
  title: {
    fontSize: 26,
    fontWeight: "700",
    color: Colors.textPrimary
  },
  clearBtn: {
    paddingVertical: 4,
    paddingHorizontal: 8
  },
  clearText: {
    fontSize: 12,
    color: "#ef4444",
    fontWeight: "600"
  },
  searchBar: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: Colors.surfaceCard,
    borderRadius: 14,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: Colors.borderSubtle,
    gap: 8,
    marginBottom: 16
  },
  searchInput: {
    flex: 1,
    color: Colors.textPrimary,
    fontSize: 14
  },
  threadItem: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: Colors.surfaceCard,
    borderRadius: 14,
    padding: 14,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: Colors.borderSubtle,
    gap: 12
  },
  threadIcon: {
    width: 36,
    height: 36,
    borderRadius: 10,
    backgroundColor: "rgba(0, 240, 255, 0.08)",
    alignItems: "center",
    justifyContent: "center"
  },
  threadDetails: {
    flex: 1
  },
  threadTitle: {
    fontSize: 14,
    fontWeight: "600",
    color: Colors.textPrimary,
    marginBottom: 4
  },
  threadDate: {
    fontSize: 11,
    color: Colors.textMuted
  },
  emptyView: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 32
  },
  emptyTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: Colors.textSecondary,
    marginTop: 12,
    marginBottom: 4
  },
  emptySubtitle: {
    fontSize: 13,
    color: Colors.textMuted,
    textAlign: "center"
  }
});
