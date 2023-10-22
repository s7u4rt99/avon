import {
  Pressable,
  SafeAreaView,
  StyleSheet,
  useColorScheme,
} from "react-native";
import { View } from "../components/Themed";
import React, { useState, useCallback, useEffect } from "react";
import {
  Composer,
  Bubble,
  GiftedChat,
  IMessage,
  InputToolbar,
  InputToolbarProps,
} from "react-native-gifted-chat";
import FontAwesome from "@expo/vector-icons/FontAwesome";
import * as Haptics from "expo-haptics";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { getChatMessages, addChatMessages } from "../firebase/realtime";
import {
  FirebaseChatMessage,
  Message,
  MessageSender,
} from "../constants/interfaces";
import axios, { all } from "axios";
import { BASE_URL } from "../constants/config";

export default function MainScreen() {
  const [messages, setMessages] = useState<Array<Message>>([]);
  const [email, setEmail] = useState<string>("");
  const colorScheme = useColorScheme();
  useEffect(() => {
    let messageUnsubscribe: () => void | undefined;
    async function asyncStuff() {
      try {
        const emailMaybe = await AsyncStorage.getItem("email");
        const email = emailMaybe || "";
        setEmail(email);
        messageUnsubscribe = await getChatMessages(email, (snapshot) => {
          const firebaseSnapshot: { [k: string]: FirebaseChatMessage } =
            snapshot.val();
          if (!firebaseSnapshot) {
            return;
          }
          const firebaseMessages = Object.entries(firebaseSnapshot)
            .filter(([k, v]) => !!v && !!k)
            .map(([id, m]) => ({
              _id: id,
              text: m.text,
              createdAt: new Date(m.sentAt),
              user: {
                _id: m.isSentByBot ? MessageSender.Bot : MessageSender.Sender,
              },
              hasBeenTypedOut: true,
            }));
          setMessages(firebaseMessages.reverse());
        });
      } catch (e) {
        alert(e);
        console.log("something went wrong when");
      }
    }
    asyncStuff();

    return () => {
      messageUnsubscribe && messageUnsubscribe();
    };
  }, []);

  async function onSend(allNewMessages: Array<Message> = []) {
    onSendUi(allNewMessages.map((m) => ({ ...m, hasBeenTypedOut: true })));

    const success = await addChatMessages(email, allNewMessages);
    if (!success) {
      console.log("failed to send message");
    }

    console.log("Sending message to server");
    const res = await axios.post(
      BASE_URL + `/reply`,
      {},
      {
        params: {
          email,
          message: allNewMessages.join("\n"),
        },
      }
    );
  }

  const onSendUi = useCallback((messages: Array<Message> = []) => {
    setMessages((previousMessages) =>
      GiftedChat.append(previousMessages, messages)
    );
  }, []);

  return (
    <SafeAreaView
      style={[
        styles.boundary,
        { backgroundColor: colorScheme === "dark" ? "#000" : "#fff" },
      ]}
    >
      <View style={styles.container}>
        <View style={styles.chatContainer}>
          <GiftedChat
            messages={messages}
            onSend={onSend}
            user={{
              _id: MessageSender.Sender,
            }}
            listViewProps={{
              keyboardDismissMode: "on-drag",
            }}
            timeTextStyle={{
              left: { color: colorScheme === "dark" ? "#000" : "#fff" },
              right: { color: colorScheme === "dark" ? "#fff" : "#000" },
            }}
            renderAvatar={null}
            renderBubble={(props) => {
              return (
                <Bubble
                  {...props}
                  wrapperStyle={{
                    left: {
                      backgroundColor: colorScheme === "dark" ? "#fff" : "#000",
                    },
                    right: {
                      backgroundColor:
                        colorScheme === "dark" ? "#262626" : "#adadad",
                    },
                  }}
                  containerStyle={{
                    left: {
                      marginBottom: "5%",
                    },
                    right: {
                      marginBottom: "5%",
                    },
                  }}
                  bottomContainerStyle={{
                    // The time below text in a bubble
                    left: {
                      paddingHorizontal: "5%",
                      marginBottom: "2%",
                    },
                    right: {
                      marginBottom: "2%",
                      paddingHorizontal: "5%",
                    },
                  }}
                  textStyle={{
                    left: {
                      paddingHorizontal: "5%",
                      paddingTop: "2%",
                      color: colorScheme === "dark" ? "#000" : "#fff",
                    },
                    right: {
                      paddingHorizontal: "5%",
                      paddingTop: "2%",
                      color: colorScheme === "dark" ? "#fff" : "#000",
                    },
                  }}
                />
              );
            }}
            renderUsernameOnMessage={false}
            renderInputToolbar={(toolbarProps: InputToolbarProps<IMessage>) => {
              return (
                <InputToolbar
                  {...toolbarProps}
                  onPressActionButton={toolbarProps.onPressActionButton}
                  renderComposer={(props) => {
                    return (
                      <Composer
                        {...props}
                        textInputAutoFocus={true}
                        textInputProps={{
                          spellCheck: true,
                        }}
                        placeholder="what's up?"
                        placeholderTextColor="gray"
                        textInputStyle={[
                          styles.textBox,
                          { color: colorScheme === "dark" ? "#fff" : "#000" },
                        ]}
                      />
                    );
                  }}
                  containerStyle={[
                    styles.textBoxContainer,
                    {
                      backgroundColor: colorScheme === "dark" ? "#000" : "#fff",
                    },
                  ]}
                  renderSend={(props) => {
                    return (
                      <Pressable
                        onPress={() => {
                          props.onSend &&
                            props.onSend({ text: props?.text?.trim() }, true);
                          Haptics.impactAsync(
                            Haptics.ImpactFeedbackStyle.Light
                          );
                        }}
                      >
                        <FontAwesome
                          name="chevron-circle-up"
                          size={30}
                          color={colorScheme === "dark" ? "#fff" : "#2e78b7"}
                          style={{ marginRight: "5%", marginBottom: "20%" }}
                        />
                      </Pressable>
                    );
                  }}
                />
              );
            }}
          />
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  boundary: {
    flex: 1,
  },
  container: {
    flex: 1,
    flexDirection: "column",
  },
  titleContainer: {
    flex: 1 / 8,
    alignItems: "center",
    justifyContent: "center",
  },
  title: {
    fontSize: 20,
    fontWeight: "bold",
  },
  separator: {
    marginVertical: 30,
    height: 1,
    width: "80%",
  },
  chatContainer: {
    flex: 8 / 8,
    marginBottom: "5%",
  },
  textBoxContainer: {},
  textBox: {
    marginTop: "5%",
    marginLeft: "5%",
  },
});
