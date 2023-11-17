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
  apiKey: "AIzaSyDLkcxVW8jLdciiv5sQpOSqdu_9iiPX8OM",
  authDomain: "nova-83407.firebaseapp.com",
  databaseURL: "https://nova-83407-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "nova-83407",
  storageBucket: "nova-83407.appspot.com",
  messagingSenderId: "247250941452",
  appId: "1:247250941452:web:abd54fc74cb68161ae2029"
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
  return "vishnu.sundaresan@gmail.com".replace(/\./g, "_");
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
