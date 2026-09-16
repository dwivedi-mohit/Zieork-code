/**
 * Grok Floating Pill Input Component
 * Features expanding text input, microphone visualizer, and glowing send button
 */

import React, { useState, useRef } from "react";
import {
  View,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Animated,
  Platform
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import * as Haptics from "expo-haptics";
import { Colors } from "../theme/colors";

export const FloatingInput = ({
  onSend,
  isGenerating = false,
  onAttach,
  mode = "regular"
}) => {
  const [text, setText] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const pulseAnim = useRef(new Animated.Value(1)).current;

  const hasText = text.trim().length > 0;
  const isFunMode = mode === "fun";

  const handleSend = () => {
    if (!hasText || isGenerating) return;
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    } catch (e) {}
    const toSend = text;
    setText("");
    onSend(toSend);
  };

  const toggleMic = () => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch (e) {}
    if (isRecording) {
      setIsRecording(false);
      pulseAnim.stopAnimation();
      pulseAnim.setValue(1);
    } else {
      setIsRecording(true);
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, { toValue: 1.3, duration: 400, useNativeDriver: true }),
          Animated.timing(pulseAnim, { toValue: 1, duration: 400, useNativeDriver: true })
        ])
      ).start();
    }
  };

  return (
    <View style={styles.outerWrapper}>
      <View style={styles.pillContainer}>
        {/* Plus / Action Icon */}
        <TouchableOpacity
          activeOpacity={0.7}
          onPress={onAttach}
          style={styles.attachBtn}
        >
          <Ionicons name="add" size={22} color={Colors.textSecondary} />
        </TouchableOpacity>

        {/* Input Text Field */}
        <TextInput
          style={styles.input}
          placeholder={isRecording ? "Listening to your voice..." : "Ask Zieork anything..."}
          placeholderTextColor={isRecording ? Colors.cyan : Colors.textMuted}
          multiline
          value={text}
          onChangeText={setText}
          keyboardAppearance="dark"
        />

        {/* Microphone Button */}
        <TouchableOpacity activeOpacity={0.7} onPress={toggleMic} style={styles.micBtn}>
          <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
            <Ionicons
              name={isRecording ? "mic" : "mic-outline"}
              size={20}
              color={isRecording ? Colors.cyan : Colors.textSecondary}
            />
          </Animated.View>
        </TouchableOpacity>

        {/* Send Button */}
        <TouchableOpacity
          activeOpacity={0.7}
          onPress={handleSend}
          disabled={!hasText || isGenerating}
          style={[styles.sendBtnWrapper, !hasText && styles.sendBtnDisabled]}
        >
          {hasText ? (
            <LinearGradient
              colors={isFunMode ? Colors.gradients.funMode : Colors.gradients.cosmicGlow}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={styles.sendBtnGradient}
            >
              <Ionicons name="arrow-up" size={17} color="#ffffff" />
            </LinearGradient>
          ) : (
            <View style={styles.sendBtnPlaceholder}>
              <Ionicons name="arrow-up" size={17} color={Colors.textDark} />
            </View>
          )}
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  outerWrapper: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    backgroundColor: Colors.background
  },
  pillContainer: {
    flexDirection: "row",
    alignItems: "flex-end",
    backgroundColor: Colors.inputBackground,
    borderRadius: 26,
    borderWidth: 1,
    borderColor: Colors.borderSubtle,
    paddingHorizontal: 8,
    paddingVertical: 6,
    gap: 6
  },
  attachBtn: {
    width: 34,
    height: 34,
    borderRadius: 17,
    alignItems: "center",
    justifyContent: "center"
  },
  input: {
    flex: 1,
    fontSize: 15,
    lineHeight: 20,
    color: Colors.textPrimary,
    maxHeight: 100,
    minHeight: 24,
    paddingTop: Platform.OS === "ios" ? 8 : 4,
    paddingBottom: Platform.OS === "ios" ? 8 : 4
  },
  micBtn: {
    width: 34,
    height: 34,
    borderRadius: 17,
    alignItems: "center",
    justifyContent: "center"
  },
  sendBtnWrapper: {
    width: 34,
    height: 34,
    borderRadius: 17,
    overflow: "hidden"
  },
  sendBtnDisabled: {
    opacity: 0.5
  },
  sendBtnGradient: {
    width: "100%",
    height: "100%",
    alignItems: "center",
    justifyContent: "center"
  },
  sendBtnPlaceholder: {
    width: "100%",
    height: "100%",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "rgba(255, 255, 255, 0.05)",
    borderRadius: 17
  }
});
