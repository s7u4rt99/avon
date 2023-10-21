import { StatusBar } from "expo-status-bar";
import { ImageBackground, Platform, StyleSheet } from "react-native";
import React, { useState } from "react";
import { View } from "../components/Themed";
import { MonoText } from "../components/StyledText";
import TypeWriter from "react-native-typewriter";
import StyledButton from "../components/StyledButton";
import { Link } from "expo-router";
const landing = require("../assets/images/landing.png");

export default function LoginScreen() {
  return (
    <View style={styles.container}>
      <ImageBackground resizeMode="cover" source={landing} style={styles.bg}>
        <View style={{ flex: 1, minWidth: "90%", paddingTop: "50%" }}>
          <StyledButton style={styles.actionButton}>
            <MonoText>Connect Google</MonoText>
          </StyledButton>
          <Link href="/landing" asChild>
            <StyledButton style={styles.actionButton}>
              <MonoText>Back</MonoText>
            </StyledButton>
          </Link>
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
    // justifyContent: "center",
  },
  title: {
    fontSize: 60,
    fontVariant: ["small-caps"],
    fontWeight: "bold",
  },
  actionButton: {
    width: "50%",
    alignSelf: "center",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: "50%",
  },
  separator: {
    marginVertical: 30,
    height: 1,
    width: "80%",
  },
});
