import React from "react";
import { StyleSheet, useColorScheme } from "react-native";

import Colors from "../constants/Colors";
import { ExternalLink } from "./ExternalLink";
import { MonoText } from "./StyledText";
import { Text, View } from "./Themed";
import StyledButton from "./StyledButton";

export default function SettingsModal() {
  const colorScheme = useColorScheme();
  const empoweringQuotes = [
    "You are capable of achieving greatness beyond your imagination. 🚀",
    "Believe in yourself, for you are stronger than you think. 💪",
    "Your potential knows no bounds; you are a force of nature. 🌟",
    "Success is your destiny, and nothing can stand in your way. 🏆",
    "The world is yours to conquer; go out and claim it! 🌎",
    "You have the power to turn your dreams into reality. ✨",
    "Every challenge you face is an opportunity for growth and triumph. 🌱",
    "You are a masterpiece in progress, always improving and evolving. 🎨",
    "Your positive mindset is your greatest asset; use it to your advantage. 🧠",
    "You are not just a part of the journey; you are the hero of your story. 🦸‍♂️"
  ];
  
  const quoteIdx = Math.random() * empoweringQuotes.length;
  const quote = empoweringQuotes[Math.floor(quoteIdx)];
  return (
    <View>
      <View style={styles.getStartedContainer}>
        <View
          style={[styles.quoteHighlightContainer, styles.homeScreenFilename]}
          darkColor="rgba(255,255,255,0.05)"
          lightColor="rgba(0,0,0,0.05)"
        >
          <Text
            style={styles.quoteText}
          >
            "{quote}"
          </Text>
        </View>

        {/* <View
          style={[styles.codeHighlightContainer, styles.homeScreenFilename]}
          darkColor="rgba(255,255,255,0.05)"
          lightColor="rgba(0,0,0,0.05)"
        >
          <MonoText>{path}</MonoText>
        </View> */}

        <StyledButton onPress={() => alert("Coming soon!")}>
          <MonoText
            style={[
              styles.quoteText,
              { color: colorScheme === "dark" ? "#fff" : "#000" },
            ]}
          >
            add a guardian angel 😇
          </MonoText>
        </StyledButton>
      </View>

      <View style={styles.helpContainer}>
        <ExternalLink
          style={styles.helpLink}
          href="https://docs.expo.io/get-started/create-a-new-app/#opening-the-app-on-your-phonetablet"
        >
          <MonoText style={styles.helpLinkText} lightColor={Colors.light.tint}>
            tap here for help
          </MonoText>
        </ExternalLink>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  getStartedContainer: {
    alignItems: "center",
    marginHorizontal: 50,
    flexDirection: "column",
    gap: 30,
  },
  homeScreenFilename: {
    marginVertical: 7,
  },
  quoteHighlightContainer: {
    borderRadius: 15,
    padding: "3%",
  },
  quoteText: {
    fontSize: 15,
    lineHeight: 24,
    textAlign: "center",
    color: "#5d5e5e",
    fontStyle: "italic",
  },
  helpContainer: {
    marginTop: 15,
    marginHorizontal: 20,
    alignItems: "center",
  },
  helpLink: {
    paddingVertical: 15,
  },
  helpLinkText: {
    textAlign: "center",
  },
});
