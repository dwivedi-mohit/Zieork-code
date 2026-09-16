/**
 * Grok Explore / Discover Screen
 * Showcases trending AI topics and Mohit Dwivedi's signature applications
 */

import React from "react";
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Linking, SafeAreaView } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { Colors } from "../theme/colors";

export const ExploreScreen = () => {
  const trendingTopics = [
    {
      id: "1",
      tag: "TRENDING IN AI",
      title: "Sovereign 1B Models Rivaling Cloud APIs",
      summary: "How Zieork Prime achieves high-speed coding and structured reasoning natively on local CPU hardware with 8-bit quantized KV caching.",
      gradient: Colors.gradients.cosmicGlow
    },
    {
      id: "2",
      tag: "ARCHITECTURE",
      title: "Sub-10ms 1,000,000+ Token Context",
      summary: "Inverted index and BM25 dynamic chunk retrieval enables infinite document capacity without exploding RAM consumption.",
      gradient: Colors.gradients.emeraldMint
    },
    {
      id: "3",
      tag: "NEURAL ENGINEERING",
      title: "Dual-Engine Edge Routing",
      summary: "NumPy microsecond transformer handles instant routing while GGUF causal decoder performs deep code synthesis.",
      gradient: Colors.gradients.funMode
    }
  ];

  const mohitApps = [
    {
      title: "hackORtech",
      role: "Founder & CEO",
      desc: "Global tech opportunities, hackathons, open-source programs, and developer career acceleration.",
      url: "https://hackortech.in",
      icon: "rocket-sharp"
    },
    {
      title: "Spex",
      role: "Creator",
      desc: "Zero-signup, peer-to-peer real-time WebRTC communications engine for instant collaboration.",
      url: "https://spex-1.onrender.com",
      icon: "videocam-sharp"
    },
    {
      title: "NFSQL",
      role: "Creator",
      desc: "Instant natural language to production SQL query generator powered by edge NLP.",
      url: "https://nfsql.mohitdwivedi.in",
      icon: "server-sharp"
    },
    {
      title: "Versant by Mohit",
      role: "Creator",
      desc: "Comprehensive speech assessment and corporate fluency simulator.",
      url: "https://versant.mohitdwivedi.in",
      icon: "mic-sharp"
    }
  ];

  const openUrl = (url) => {
    Linking.openURL(url).catch((e) => console.warn(e));
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.pageTitle}>Discover</Text>
          <Text style={styles.pageSubtitle}>The Sovereign Edge Frontier</Text>
        </View>

        {/* Trending Section */}
        <Text style={styles.sectionHeader}>Trending Now</Text>
        {trendingTopics.map((item) => (
          <View key={item.id} style={styles.trendingCard}>
            <View style={styles.trendingTagRow}>
              <Text style={styles.tagText}>{item.tag}</Text>
            </View>
            <Text style={styles.cardTitle}>{item.title}</Text>
            <Text style={styles.cardSummary}>{item.summary}</Text>
          </View>
        ))}

        {/* Mohit Dwivedi Projects Showcase */}
        <Text style={[styles.sectionHeader, { marginTop: 24 }]}>
          Built by Mohit Dwivedi
        </Text>
        <Text style={styles.sectionSubtext}>
          15+ Production Applications across WebRTC, AI, and Cloud
        </Text>

        <View style={styles.appsGrid}>
          {mohitApps.map((app, index) => (
            <TouchableOpacity
              key={index}
              activeOpacity={0.8}
              onPress={() => openUrl(app.url)}
              style={styles.appCard}
            >
              <View style={styles.appIconWrapper}>
                <Ionicons name={app.icon} size={20} color={Colors.cyan} />
              </View>
              <Text style={styles.appTitle}>{app.title}</Text>
              <Text style={styles.appRole}>{app.role}</Text>
              <Text style={styles.appDesc}>{app.desc}</Text>
              <View style={styles.launchRow}>
                <Text style={styles.launchText}>Open App</Text>
                <Ionicons name="arrow-forward" size={12} color={Colors.cyan} />
              </View>
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: Colors.background
  },
  container: {
    padding: 16,
    paddingBottom: 28
  },
  header: {
    marginBottom: 20
  },
  pageTitle: {
    fontSize: 26,
    fontWeight: "700",
    color: Colors.textPrimary
  },
  pageSubtitle: {
    fontSize: 14,
    color: Colors.textMuted,
    marginTop: 2
  },
  sectionHeader: {
    fontSize: 17,
    fontWeight: "700",
    color: Colors.textPrimary,
    marginBottom: 8
  },
  sectionSubtext: {
    fontSize: 12,
    color: Colors.textMuted,
    marginBottom: 14
  },
  trendingCard: {
    backgroundColor: Colors.surfaceCard,
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: Colors.borderSubtle
  },
  trendingTagRow: {
    marginBottom: 6
  },
  tagText: {
    fontSize: 10,
    fontWeight: "700",
    letterSpacing: 0.8,
    color: Colors.cyan
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: Colors.textPrimary,
    marginBottom: 6,
    lineHeight: 22
  },
  cardSummary: {
    fontSize: 13,
    lineHeight: 19,
    color: Colors.textSecondary
  },
  appsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 12,
    justifyContent: "space-between"
  },
  appCard: {
    width: "48%",
    backgroundColor: Colors.surfaceCard,
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: Colors.borderSubtle
  },
  appIconWrapper: {
    width: 36,
    height: 36,
    borderRadius: 10,
    backgroundColor: "rgba(0, 240, 255, 0.1)",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 10
  },
  appTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: Colors.textPrimary
  },
  appRole: {
    fontSize: 11,
    color: Colors.purple,
    fontWeight: "600",
    marginBottom: 6
  },
  appDesc: {
    fontSize: 11,
    color: Colors.textMuted,
    lineHeight: 16,
    marginBottom: 12
  },
  launchRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    marginTop: "auto"
  },
  launchText: {
    fontSize: 11,
    fontWeight: "600",
    color: Colors.cyan
  }
});
