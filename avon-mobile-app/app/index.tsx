import { StatusBar } from "expo-status-bar";
import { MonoText } from "../components/StyledText";
import TypeWriter from "react-native-typewriter";
import StyledButton from "../components/StyledButton";
import { Link, useRouter } from "expo-router";
import React, { useEffect, useState } from "react";
import { View, Platform, ImageBackground, StyleSheet } from "react-native";
import * as Device from "expo-device";
import * as Notifications from "expo-notifications";
import Constants from "expo-constants";
import AsyncStorage from "@react-native-async-storage/async-storage";

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: false,
    shouldSetBadge: false,
  }),
});

// Can use this function below or use Expo's Push Notification Tool from: https://expo.dev/notifications
async function sendPushNotification(
  expoPushToken: Notifications.ExpoPushToken
) {
  const message = {
    to: expoPushToken,
    sound: "default",
    title: "Original Title",
    body: "And here is the body!",
    data: { someData: "goes here" },
  };

  await fetch("https://exp.host/--/api/v2/push/send", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Accept-encoding": "gzip, deflate",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(message),
  });
}

async function registerForPushNotificationsAsync() {
  let token;

  if (Platform.OS === "android") {
    Notifications.setNotificationChannelAsync("default", {
      name: "default",
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: "#FF231F7C",
    });
  }

  if (Device.isDevice) {
    const { status: existingStatus } =
      await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;
    if (existingStatus !== "granted") {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }
    if (finalStatus !== "granted") {
      alert("Failed to get push token for push notification!");
      return;
    }
    token = await Notifications.getExpoPushTokenAsync({
      projectId: Constants.expoConfig!.extra!.eas!.projectId!,
    });
    console.log("EXPO TOKEN NEEDED", token);
  } else {
    alert("Must use physical device for Push Notifications");
  }

  return token;
}

const landing = require("../assets/images/landing.png");

function TypewriterComponent({ children }: { children?: React.ReactNode }) {
  const [direction, setDirection] = useState<1 | -1>(1);
  const linesToShow = ["Hi,\nI'm Nova!", "Your Personal Co-pilot"];
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
  // const [expoPushToken, setExpoPushToken] = useState<
  //   Notifications.ExpoPushToken | undefined
  // >(undefined);
  // const [notification, setNotification] = useState<
  //   Notifications.Notification | undefined
  // >(undefined);
  // const notificationListener = useRef<Notifications.Subscription>();
  // const responseListener = useRef<Notifications.Subscription>();

  // useEffect(() => {
  //   async function asyncStuff() {
  //     const token = await registerForPushNotificationsAsync();
  //     if (token) {
  //       setExpoPushToken(token);
  //     }

  //     notificationListener.current =
  //       Notifications.addNotificationReceivedListener((notification) => {
  //         setNotification(notification);
  //       });

  //     responseListener.current =
  //       Notifications.addNotificationResponseReceivedListener((response) => {
  //         console.log(response);
  //       });
  //   }
  //   asyncStuff();

  //   return () => {
  //     if (notificationListener.current) {
  //       Notifications.removeNotificationSubscription(
  //         notificationListener.current
  //       );
  //     }
  //     if (responseListener.current) {
  //       Notifications.removeNotificationSubscription(responseListener.current);
  //     }
  //   };
  // }, []);

  const router = useRouter();
  useEffect(() => {
    async function asyncStuff() {
      const email = await AsyncStorage.getItem("email");
      if (email) {
        router.push("/main");
      }
    }
    asyncStuff();

    return () => {
      // cleanup
      AsyncStorage.clear();
    };
  }, []);

  return (
    <View style={styles.container}>
      <ImageBackground resizeMode="cover" source={landing} style={styles.bg}>
        <View
          style={{
            flex: 1,
            paddingTop: "50%",
            paddingHorizontal: "5%",
          }}
        >
          <TypewriterComponent />
        </View>
        <Link href="/main" asChild>
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
  },
  bg: {
    flex: 1,
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
