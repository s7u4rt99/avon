import { StatusBar } from "expo-status-bar";
import {
  ImageBackground,
  NativeSyntheticEvent,
  NativeTouchEvent,
  Platform,
  StyleSheet,
  TextInput,
  useColorScheme,
} from "react-native";
import React, { useEffect, useState } from "react";
import { View } from "../components/Themed";
import { MonoText } from "../components/StyledText";
import StyledButton from "../components/StyledButton";
import { useRouter } from "expo-router";
import * as WebBrowser from "expo-web-browser";
import TypeWriter from "react-native-typewriter";
import axios from "axios";
import { BASE_URL } from "../constants/config";
const landing = require("../assets/images/landing.png");

export default function LoginScreen() {
  const router = useRouter();
  const colorScheme = useColorScheme();
  const [email, setEmail] = useState<string>("");
  const [showAll, setShowAll] = useState(false);
  const [isGoogleConnected, setIsGoogleConnected] = useState<boolean>(false);

  async function connectToGoogle(e: NativeSyntheticEvent<NativeTouchEvent>) {
    // Prevent the default behavior of linking to the default browser on native.
    e.preventDefault();
    try {
      const authUrlResponse = await axios.get<string>(
        BASE_URL +
          `/get_google_oauth_url${email ? `?email=${email.toLowerCase()}` : ""}`
      );
      if (authUrlResponse.status === 200 && authUrlResponse.data) {
        if (Platform.OS !== "web") {
          // Open the link in an in-app browser.
          WebBrowser.openBrowserAsync(authUrlResponse.data as string);
        }
      }
    } catch (e) {
      if (e instanceof Error) {
        console.error(e.name, e.message);
      }
    }
  }

  const checkUserConnectedGoogle = async () => {
    try {
      const emailResponse = await axios.get<string>(
        BASE_URL + "/users/email/" + email.toLowerCase()
      );
      if (emailResponse.status === 200 && emailResponse.data) {
        setIsGoogleConnected(true);
      }
    } catch (e) {
      if (e instanceof Error) {
        console.warn(e.name, e.message);
      }
    }
  };
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
                  setTimeout(() => {
                    setShowAll(true);
                  }, 200);
                }}
              >
                We'll need you to connect the following to get you started
              </TypeWriter>
            </MonoText>
          </View>
          {showAll && (
            <View style={{ minWidth: "90%", gap: 4 }}>
              <TextInput
                style={[
                  {
                    backgroundColor: colorScheme === "dark" ? "#000" : "#fff",
                    color: colorScheme === "dark" ? "#fff" : "#000",
                  },
                  styles.input,
                ]}
                onChangeText={(text) => setEmail(text)}
                keyboardType="email-address"
                placeholder="Enter your email"
              />
              <StyledButton
                style={styles.actionButton}
                disabled={!email}
                onPress={connectToGoogle}
              >
                <MonoText>
                  {isGoogleConnected ? "Connected to Google" : "Connect Google"}
                </MonoText>
              </StyledButton>
              <StyledButton
                style={styles.actionButton}
                onPress={checkUserConnectedGoogle}
              >
                <MonoText>Refresh</MonoText>
              </StyledButton>
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
  input: {
    alignSelf: "center",
    alignItems: "center",
    justifyContent: "center",
    width: "100%",
    height: 40,
    borderColor: "gray",
    borderWidth: 1,
    borderRadius: 5,
    padding: 10,
    marginBottom: 10,
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
