import { IMessage } from "react-native-gifted-chat";

export interface FirebaseChatMessage {
  isSentByBot: boolean;
  text: string;
  sentAt: string; // ISO 8601
  id: string | number;
  callback?: string;
}

export interface Message extends IMessage {
  hasBeenTypedOut?: boolean;
}

export enum MessageSender {
  Bot,
  Sender
}
