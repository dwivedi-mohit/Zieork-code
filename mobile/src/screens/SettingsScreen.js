/**
 * Grok Engine & Settings Screen
 * LAN backend configuration, model switcher, and Mohit Dwivedi VIP Creator Card
 */

import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Linking,
  SafeAreaView
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import * as Haptics from "expo-haptics";
import { Colors } from "../theme/colors";
import { getStoredServerUrl, setStoredServerUrl } from "../services/api";

export const SettingsScreen = () => {
  const [serverUrl, setServerUrl] = useState("http://localhost:5000");
  const [connectionStatus, setConnectionStatus] = useState(null); // null | 'ok' | 'error'
  const [selectedModel, setSelectedModel] = useState("prime");

  useEffect(() => {
    getStoredServerUrl().then((url) => setServerUrl(url));
  }, []);

  const handleSaveUrl = async () => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch (e) {}
    await setStoredServerUrl(serverUrl);
    testConnection();
  };

  const testConnection = async () => {
    setConnectionStatus("testing");
    try {
      const res = await fetch(`${serverUrl}/api/model/status`);
      if (res.ok) {
        setConnectionStatus("ok");
        try {
          Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        } catch (e) {}
      } else {
        setConnectionStatus("error");
      }
    } catch (e) {
      setConnectionStatus("error");
    }
  };

  const openUrl = (url) => {
    Linking.openURL(url).catch((e) => console.warn(e));
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Engine</Text>
          <Text style={styles.subtitle}>Sovereign AI Runtime & Settings</Text>
        </View>

        {/* Server Connection Card */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Local Backend Host</Text>
          <Text style={styles.cardDesc}>
            Enter your computer's local Wi-Fi IP (e.g. http://192.168.1.5:5000) to chat with Zieork Prime from your phone.
          </Text>

          <View style={styles.inputRow}>
            <TextInput
              style={styles.urlInput}
              value={serverUrl}
              onChangeText={setServerUrl}
              placeholder="http://192.168.x.x:5000"
              placeholderTextColor={Colors.textMuted}
              autoCapitalize="none"
              autoCorrect={false}
              keyboardAppearance="dark"
            />
            <TouchableOpacity activeOpacity={0.7} onPress={handleSaveUrl} style={styles.saveBtn}>
              <Text style={styles.saveBtnText}>Save</Text>
            </TouchableOpacity>
          </View>

          {connectionStatus === "testing" && (
            <Text style={styles.statusTesting}>Connecting to Zieork server...</Text>
          )}
          {connectionStatus === "ok" && (
            <View style={styles.statusOkRow}>
              <Ionicons name="checkmark-circle" size={14} color={Colors.emerald} />
              <Text style={styles.statusOkText}>Connected to Sovereign Core</Text>
            </View>
          )}
          {connectionStatus === "error" && (
            <View style={styles.statusErrorRow}>
              <Ionicons name="alert-circle" size={14} color="#ef4444" />
              <Text style={styles.statusErrorText}>Could not reach server. Verify host IP and port 5000.</Text>
            </View>
          )}
        </View>

        {/* Model Tiers Card */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Active Model Tier</Text>
          <TouchableOpacity
            activeOpacity={0.7}
            onPress={() => setSelectedModel("prime")}
            style={[styles.tierRow, selectedModel === "prime" && styles.tierRowActive]}
          >
            <View style={styles.tierDot} />
            <View style={styles.tierInfo}>
              <Text style={styles.tierName}>Zieork Prime (1.23B)</Text>
              <Text style={styles.tierSub}>GGUF Deep Causal Decoder • 4,096 Context</Text>
            </View>
            {selectedModel === "prime" && (
              <Ionicons name="checkmark-circle" size={18} color={Colors.cyan} />
            )}
          </TouchableOpacity>

          <TouchableOpacity
            activeOpacity={0.7}
            onPress={() => setSelectedModel("micro")}
            style={[styles.tierRow, selectedModel === "micro" && styles.tierRowActive]}
          >
            <View style={[styles.tierDot, { backgroundColor: Colors.purple }]} />
            <View style={styles.tierInfo}>
              <Text style={styles.tierName}>Zieork Micro (306K)</Text>
              <Text style={styles.tierSub}>Pure NumPy Tensor Kernel • Sub-millisecond</Text>
            </View>
            {selectedModel === "micro" && (
              <Ionicons name="checkmark-circle" size={18} color={Colors.cyan} />
            )}
          </TouchableOpacity>
        </View>

        {/* 1M+ Infinite Context Engine */}
        <View style={styles.card}>
          <View style={styles.badgeHeader}>
            <Text style={styles.cardTitle}>1M+ Context Engine</Text>
            <View style={styles.activeBadge}>
              <Text style={styles.activeBadgeText}>ACTIVE</Text>
            </View>
          </View>
          <Text style={styles.cardDesc}>
            Dynamic BM25 SQLite Inverted Index with sub-10ms retrieval latency across local codebases and documents.
          </Text>
        </View>

        {/* VIP Creator Profile Card: Mohit Dwivedi */}
        <View style={styles.creatorCardWrapper}>
          <LinearGradient
            colors={Colors.gradients.cardSurface}
            style={styles.creatorGradientCard}
          >
            <View style={styles.creatorTopRow}>
              <View style={styles.creatorAvatarWrapper}>
                <LinearGradient
                  colors={Colors.gradients.cosmicGlow}
                  style={styles.creatorAvatarGradient}
                >
                  <Text style={styles.avatarInitials}>MD</Text>
                </LinearGradient>
              </View>
              <View style={styles.creatorHeaderDetails}>
                <View style={styles.nameRow}>
                  <Text style={styles.creatorName}>Mohit Dwivedi</Text>
                  <Ionicons name="shield-checkmark" size={15} color={Colors.cyan} />
                </View>
                <Text style={styles.creatorRoleText}>Sole Creator, Developer & Owner</Text>
                <Text style={styles.creatorLocationText}>Karkeli, Umaria, MP, India</Text>
              </View>
            </View>

            <Text style={styles.creatorBio}>
              Full-Stack & AI Software Developer, Founder & CEO of hackORtech, and HCL Tech Scholar. Specialized in enterprise architecture, model orchestration, and edge intelligence.
            </Text>

            {/* Quick Action Links */}
            <View style={styles.creatorLinkGrid}>
              <TouchableOpacity
                activeOpacity={0.7}
                onPress={() => openUrl("https://mohitdwivedi.in")}
                style={styles.creatorLinkPill}
              >
                <Ionicons name="globe-outline" size={13} color={Colors.cyan} />
                <Text style={styles.linkPillText}>Portfolio</Text>
              </TouchableOpacity>

              <TouchableOpacity
                activeOpacity={0.7}
                onPress={() => openUrl("https://hackortech.in")}
                style={styles.creatorLinkPill}
              >
                <Ionicons name="rocket-outline" size={13} color={Colors.purple} />
                <Text style={styles.linkPillText}>hackORtech</Text>
              </TouchableOpacity>

              <TouchableOpacity
                activeOpacity={0.7}
                onPress={() => openUrl("https://github.com/dwivedi-mohit")}
                style={styles.creatorLinkPill}
              >
                <Ionicons name="logo-github" size={13} color={Colors.textPrimary} />
                <Text style={styles.linkPillText}>GitHub</Text>
              </TouchableOpacity>

              <TouchableOpacity
                activeOpacity={0.7}
                onPress={() => openUrl("mailto:mohitdwivedi633@gmail.com")}
                style={styles.creatorLinkPill}
              >
                <Ionicons name="mail-outline" size={13} color={Colors.emerald} />
                <Text style={styles.linkPillText}>Email</Text>
              </TouchableOpacity>
            </View>
          </LinearGradient>
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
    paddingBottom: 32
  },
  header: {
    marginBottom: 20
  },
  title: {
    fontSize: 26,
    fontWeight: "700",
    color: Colors.textPrimary
  },
  subtitle: {
    fontSize: 14,
    color: Colors.textMuted,
    marginTop: 2
  },
  card: {
    backgroundColor: Colors.surfaceCard,
    borderRadius: 16,
    padding: 16,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: Colors.borderSubtle
  },
  cardTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: Colors.textPrimary,
    marginBottom: 4
  },
  cardDesc: {
    fontSize: 12,
    color: Colors.textMuted,
    lineHeight: 18,
    marginBottom: 12
  },
  inputRow: {
    flexDirection: "row",
    gap: 8
  },
  urlInput: {
    flex: 1,
    backgroundColor: Colors.inputBackground,
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 13,
    color: Colors.textPrimary,
    borderWidth: 1,
    borderColor: Colors.borderSubtle
  },
  saveBtn: {
    backgroundColor: Colors.cyan,
    borderRadius: 10,
    paddingHorizontal: 16,
    alignItems: "center",
    justifyContent: "center"
  },
  saveBtnText: {
    fontSize: 13,
    fontWeight: "700",
    color: "#000000"
  },
  statusTesting: {
    fontSize: 11,
    color: Colors.cyan,
    marginTop: 8
  },
  statusOkRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    marginTop: 8
  },
  statusOkText: {
    fontSize: 12,
    color: Colors.emerald,
    fontWeight: "600"
  },
  statusErrorRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    marginTop: 8
  },
  statusErrorText: {
    fontSize: 12,
    color: "#ef4444"
  },
  tierRow: {
    flexDirection: "row",
    alignItems: "center",
    padding: 12,
    borderRadius: 12,
    backgroundColor: Colors.inputBackground,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: "transparent",
    gap: 10
  },
  tierRowActive: {
    borderColor: Colors.cyan,
    backgroundColor: "rgba(0, 240, 255, 0.05)"
  },
  tierDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: Colors.cyan
  },
  tierInfo: {
    flex: 1
  },
  tierName: {
    fontSize: 13,
    fontWeight: "600",
    color: Colors.textPrimary
  },
  tierSub: {
    fontSize: 11,
    color: Colors.textMuted,
    marginTop: 2
  },
  badgeHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 4
  },
  activeBadge: {
    backgroundColor: "rgba(16, 185, 129, 0.15)",
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6
  },
  activeBadgeText: {
    fontSize: 10,
    fontWeight: "700",
    color: Colors.emerald
  },
  creatorCardWrapper: {
    borderRadius: 18,
    overflow: "hidden",
    borderWidth: 1,
    borderColor: "rgba(0, 240, 255, 0.3)",
    marginTop: 4
  },
  creatorGradientCard: {
    padding: 16
  },
  creatorTopRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    marginBottom: 12
  },
  creatorAvatarWrapper: {
    width: 44,
    height: 44,
    borderRadius: 22,
    overflow: "hidden"
  },
  creatorAvatarGradient: {
    width: "100%",
    height: "100%",
    alignItems: "center",
    justifyContent: "center"
  },
  avatarInitials: {
    fontSize: 16,
    fontWeight: "800",
    color: "#ffffff"
  },
  creatorHeaderDetails: {
    flex: 1
  },
  nameRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6
  },
  creatorName: {
    fontSize: 15,
    fontWeight: "700",
    color: Colors.textPrimary
  },
  creatorRoleText: {
    fontSize: 11,
    color: Colors.cyan,
    fontWeight: "600",
    marginTop: 2
  },
  creatorLocationText: {
    fontSize: 11,
    color: Colors.textMuted
  },
  creatorBio: {
    fontSize: 12,
    lineHeight: 18,
    color: Colors.textSecondary,
    marginBottom: 14
  },
  creatorLinkGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8
  },
  creatorLinkPill: {
    flexDirection: "row",
    alignItems: "center",
    gap: 5,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 14,
    backgroundColor: "rgba(255, 255, 255, 0.05)",
    borderWidth: 1,
    borderColor: Colors.borderSubtle
  },
  linkPillText: {
    fontSize: 11,
    fontWeight: "600",
    color: Colors.textPrimary
  }
});
