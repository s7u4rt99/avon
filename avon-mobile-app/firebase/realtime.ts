import { initializeApp } from "firebase/app";
import {
  getDatabase,
  ref,
  push,
  set,
  onValue,
  DataSnapshot,
} from "firebase/database";
import {
  FirebaseChatMessage,
  Message,
  MessageSender,
} from "../constants/interfaces";

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

export async function addChatMessage(email: string, message: Message) {
  const chatMessageListRef = ref(db, "chats/" + email);
  const newMessageRef = await push(chatMessageListRef);
  await set(newMessageRef, {
    isSentByBot: message.user._id !== MessageSender.Sender,
    text: message.text,
    sentAt:
      typeof message.createdAt === "number"
        ? new Date(message.createdAt).toISOString()
        : message.createdAt.toISOString(),
    id: newMessageRef.key,
  } as FirebaseChatMessage);
}

function emailToKey(email: string) {
  // Replace all dots with underscores
  return email.replace(/\./g, "_");
}

export async function addChatMessages(
  uncleanEmail: string,
  messages: Message[]
) {
  const email = emailToKey(uncleanEmail);

  const results = await Promise.allSettled(
    messages.map((m) => addChatMessage(email, m))
  );

  const rejected = results.filter((r) => r.status === "rejected");
  if (rejected.length > 0) {
    console.error("Failed to add chat messages: ", rejected);
  }
  const fulfilled = results.filter((r) => r.status === "fulfilled");
  if (fulfilled.length > 0) {
    console.log("Added chat messages: ", fulfilled);
  }

  return fulfilled.length > 0 && rejected.length === 0;
}

export async function getChatMessages(
  uncleanEmail: string,
  onValueCallback: (snapshot: DataSnapshot) => void
) {
  const email = emailToKey(uncleanEmail);
  const chatMessageListRef = ref(db, "chats/" + email);
  return onValue(chatMessageListRef, onValueCallback);
}
