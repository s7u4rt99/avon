import { initializeApp } from "firebase/app";
import {
  getDatabase,
  ref,
  push,
  set,
  onValue,
  DataSnapshot,
} from "firebase/database";
import { FirebaseChatMessage, Message, MessageSender } from "../constants/interfaces";
import { uuid } from 'uuidv4';

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: process.env.FIREBASE_CHAT_API_KEY,
  authDomain: "avon-402721.firebaseapp.com",
  databaseURL: "https://avon-402721-default-rtdb.firebaseio.com",
  projectId: "avon-402721",
  storageBucket: "avon-402721.appspot.com",
  messagingSenderId: "546498726861",
  appId: "1:546498726861:web:4a59d2f673b464a00b9284",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getDatabase(app);

export async function addChatMessage(email: string, message: string) {
  const chatMessageListRef = ref(db, "chats/" + email);
  const newMessageRef = await push(chatMessageListRef);
  set(newMessageRef, {
    isSentByBot: email !== "avon-bot",
    text: message,
    sentAt: new Date().toISOString(),
    id: uuid(),
  } as FirebaseChatMessage);
}

function emailToKey(email: string) {
  // Replace all dots with underscores
  return email.replace(/\./g, "_");
}

export async function setChatMessages(uncleanEmail: string, messages: Message[]) {
  const email = emailToKey(uncleanEmail);
  const chatMessageListRef = ref(db, "chats/" + email);
  set(
    chatMessageListRef,
    messages.map((message) => ({
      isSentByBot: message.user._id !== MessageSender.Sender,
      text: message.text,
      sentAt: message.createdAt,
      id: message._id,
    }))
  );
}

export async function getChatMessages(
  uncleanEmail: string,
  onValueCallback: (snapshot: DataSnapshot) => void
) {
  const email = emailToKey(uncleanEmail);
  const chatMessageListRef = ref(db, "chats/" + email);
  return onValue(chatMessageListRef, onValueCallback);
}
