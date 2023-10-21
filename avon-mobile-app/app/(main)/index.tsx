import {
  Pressable,
  SafeAreaView,
  StyleSheet,
  useColorScheme,
} from "react-native";
import { Text, View } from "../../components/Themed";
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
import Colors from "../../constants/Colors";

interface Message extends IMessage {
  hasBeenTypedOut: boolean;
}

export default function MainScreen() {
  const [messages, setMessages] = useState<Array<Message>>([]);
  const colorScheme = useColorScheme();
  useEffect(() => {
    setMessages([
      {
        _id: 2,
        text: "Hello developer back",
        createdAt: new Date(),
        user: {
          _id: 1,
          name: "React Native",
          avatar: "https://placeimg.com/140/140/any",
        },
        hasBeenTypedOut: false,
      },
      {
        _id: 1,
        text: "Hello developer!",
        createdAt: new Date(),
        user: {
          _id: 2,
          name: "React Native",
          avatar: "https://placeimg.com/140/140/any",
        },
        hasBeenTypedOut: false,
      },
    ]);
  }, []);

  const onSend = useCallback((messages: Array<Message> = []) => {
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
        {/* <View style={styles.titleContainer}>
          <Text style={styles.title}>avon chat</Text>
        </View> */}
        <View style={styles.chatContainer}>
          <GiftedChat
            messages={messages}
            onSend={(messages) =>
              onSend(messages.map((m) => ({ ...m, hasBeenTypedOut: true })))
            }
            user={{
              _id: 1,
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
                        textInputStyle={[styles.textBox, { color: colorScheme === "dark" ? "#fff" : "#000" }]}
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
