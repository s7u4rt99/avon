import { StatusBar } from "expo-status-bar";
import { ImageBackground, Platform, StyleSheet } from "react-native";
import React, { useState } from "react";
import { View } from "../components/Themed";
import { MonoText } from "../components/StyledText";
import TypeWriter from "react-native-typewriter";
import StyledButton from "../components/StyledButton";
import { Link } from "expo-router";
const landing = require("../assets/images/landing.png");

function TypewriterComponent({ children }: { children?: React.ReactNode }) {
  const [direction, setDirection] = useState<1 | -1>(1);
  const linesToShow = ["Hi,\nI'm Avon!", "Your personal assistant"];
  const [lineIdxToShow, setLineIdxToShow] = useState<number>(0);
  return (
    <View>
      <MonoText style={styles.title}>
        <TypeWriter
          fixed
          typing={direction}
          initialDelay={300}
          onTypingEnd={() => {
            setTimeout(() => {
              setDirection(direction === -1 ? 1 : -1);
            }, 500);
            if (direction === -1) {
              setLineIdxToShow((lineIdxToShow + 1) % linesToShow.length);
            }
          }}
        >
          {linesToShow?.[lineIdxToShow]}
        </TypeWriter>
      </MonoText>
    </View>
  );
}

export default function LandingScreen() {
  return (
    <View style={styles.container}>
      <ImageBackground resizeMode="cover" source={landing} style={styles.bg}>
        <View style={{ flex: 1, minWidth: "90%", paddingTop: "50%" }}>
          <TypewriterComponent />
        </View>
        <Link href="/login" asChild>
          <StyledButton
            style={{
              width: "50%",
              alignSelf: "center",
              alignItems: "center",
              justifyContent: "center",
              marginBottom: "50%",
            }}
          >
            <MonoText>Continue</MonoText>
          </StyledButton>
        </Link>
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
  separator: {
    marginVertical: 30,
    height: 1,
    width: "80%",
  },
});
