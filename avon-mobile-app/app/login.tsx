import { StatusBar } from "expo-status-bar";
import { ImageBackground, Platform, StyleSheet } from "react-native";
import React from "react";
import { View } from "../components/Themed";
import { MonoText } from "../components/StyledText";
import StyledButton from "../components/StyledButton";
import { useRouter } from "expo-router";
import { ExternalLink } from "../components/ExternalLink";
const landing = require("../assets/images/landing.png");

export default function LoginScreen() {
  const router = useRouter();
  return (
    <View style={styles.container}>
      <ImageBackground resizeMode="cover" source={landing} style={styles.bg}>
        <View
          style={{
            flex: 1,
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <View style={styles.subtitleContainer}>
            <MonoText style={styles.subtitle}>
              We'll need you to connect the following to get you started
            </MonoText>
          </View>
          <View style={{ minWidth: "90%", gap: 4 }}>
            <ExternalLink href="https://www.google.com" asChild style={styles.actionButton}>
              <StyledButton style={styles.actionButton}>
                <MonoText>Connect Google</MonoText>
              </StyledButton>
            </ExternalLink>
            <StyledButton
              onPress={() => router.canGoBack() && router.back()}
              style={styles.actionButton}
            >
              <MonoText>Back</MonoText>
            </StyledButton>
          </View>
        </View>
        <StatusBar style={Platform.OS === "ios" ? "light" : "auto"} />
      </ImageBackground>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  bg: {
    flex: 1,
  },
  title: {
    fontSize: 60,
    fontVariant: ["small-caps"],
    fontWeight: "bold",
  },
  subtitle: {
    fontSize: 15,
    fontStyle: "italic",
  },
  subtitleContainer: {
    maxWidth: "80%",
    marginBottom: "5%",
  },
  actionButton: {
    width: "50%",
    alignSelf: "center",
    alignItems: "center",
    justifyContent: "center",
  },
  separator: {
    marginVertical: 30,
    height: 1,
    width: "80%",
  },
});
