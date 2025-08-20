export interface VideoData {
  id: string;
  video_id: string;
  title: string;
  description: string;
  date_created: string;
}

export interface Message {
  id: string;
  created_at: string;
  content: string;
  role: "user" | "assistant";
  video_id: string;
}

export interface NewMessageData {
  video_id: string;
  query: string;
}