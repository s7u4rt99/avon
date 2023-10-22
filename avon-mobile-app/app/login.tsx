import { StatusBar } from "expo-status-bar";
import { ImageBackground, Platform, StyleSheet } from "react-native";
import React, { useEffect, useState } from "react";
import { View } from "../components/Themed";
import { MonoText } from "../components/StyledText";
import StyledButton from "../components/StyledButton";
import { useRouter } from "expo-router";
import { ExternalLink } from "../components/ExternalLink";
import TypeWriter from "react-native-typewriter";
import axios from "axios";
import { BASE_URL } from "../constants/config";
const landing = require("../assets/images/landing.png");

export default function LoginScreen() {
  const router = useRouter();
  const [showAll, setShowAll] = useState(false);
  const [googleOauthUrl, setGoogleOauthUrl] = useState<string>("");

  useEffect(() => {
    async function init() {
      try {
        const authUrlResponse = await axios.get<string>(
          BASE_URL + "/get_google_oauth_url"
        );
        if (authUrlResponse.status === 200 && authUrlResponse.data) {
          setGoogleOauthUrl(authUrlResponse.data);
        }
      } catch (e) {
        if (e instanceof Error) {
          console.error(e.name, e.message);
        }
      }
    }
    init();
  }, []);
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
              <TypeWriter
                fixed
                typing={1}
                maxDelay={10}
                onTypingEnd={() => {
                  setShowAll(true);
                }}
              >
                We'll need you to connect the following to get you started
              </TypeWriter>
            </MonoText>
          </View>
          {showAll && (
            <View style={{ minWidth: "90%", gap: 4 }}>
              <ExternalLink
                href={googleOauthUrl}
                asChild
                style={styles.actionButton}
              >
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
          )}
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
