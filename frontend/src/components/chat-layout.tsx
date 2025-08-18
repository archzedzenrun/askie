import { useState, useEffect } from "react"
import { VideoList } from "./video-list"
import { ChatArea } from "./chat-area"
import { getVideos } from "@/services/videosService"
import type { VideoData } from "@/types/types"
import { getMessages } from "@/services/videosService"

export interface VideoConversation {
  id: string
  title: string
  description?: string
  videoId: string
  lastQuery?: string
}

export interface Message {
  id: string
  content: string
  sender: "user" | "assistant"
  timestamp: string
}

// Mock data for demonstration
const mockConversations: VideoConversation[] = [
  {
    id: "1",
    title: "Introduction to Machine Learning",
    description: "Basic concepts and algorithms",
    videoId: "dQw4w9WgXcQ",
    lastQuery: "What is supervised learning?",
  },
  {
    id: "2",
    title: "React Hooks Deep Dive",
    description: "Advanced React patterns",
    videoId: "abc123def456",
    lastQuery: "How does useEffect work?",
  },
  {
    id: "3",
    title: "Database Design Principles",
    videoId: "xyz789uvw012",
    lastQuery: "What is normalization?",
  },
]

const mockMessages: Message[] = [
    {
      id: "1",
      content: "What is supervised learning?",
      sender: "user",
      timestamp: "10:30 AM",
    },
    {
      id: "2",
      content:
        "Supervised learning is a type of machine learning where the algorithm learns from labeled training data. In the video, it's explained as a method where you provide the model with input-output pairs, allowing it to learn the mapping function between inputs and desired outputs.",
      sender: "assistant",
      timestamp: "10:30 AM",
    },
  ]
//   "2": [
//     {
//       id: "1",
//       content: "How does useEffect work?",
//       sender: "user",
//       timestamp: "9:15 AM",
//     },
//     {
//       id: "2",
//       content:
//         "According to the video transcript, useEffect is a React Hook that lets you perform side effects in function components. It serves the same purpose as componentDidMount, componentDidUpdate, and componentWillUnmount combined in React class components.",
//       sender: "assistant",
//       timestamp: "9:16 AM",
//     },
//   ],
// }

export function ChatLayout() {
  const [selectedVideo, setSelectedVideo] = useState<VideoData | null>(null)
  // const [conversations, setConversations] = useState<VideoConversation[]>(mockConversations)
  const [messages, setMessages] = useState<Message[]>([])
  const [videos, setVideos] = useState<VideoData[]>([])

  useEffect(() => {
    const fetchVideos = async () => {
      try {
        const request = await getVideos()
        const videoData = request.data

        setVideos(videoData)
        console.log("Fetched Videos:", videoData)
        //setSelectedVideo(videoData[0].id) // Set the first video as selected
      } catch (error) {
        console.error("Error fetching Videos:", error)
      }
     }
     
    fetchVideos()
  }, [])
      // Assuming the API returns an array of VideoData
        // Assuming Videos are in the same format as VideoConversation})

  const handleSendMessage = (content: string) => {
    // if (!selectedVideo) return

    // const newMessage: Message = {
    //   id: Date.now().toString(),
    //   content,
    //   sender: "user",
    //   timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    // }

    // setMessages((prev) => ({
    //   ...prev,
    //   [selectedVideo]: [...(prev[selectedVideo] || []), newMessage],
    // }))

    // setVideos((prev) =>
    //   prev.map((conv) => (conv.id === selectedVideo ? { ...conv, lastQuery: content } : conv)),
    // )

    // // Simulate AI response (in real app, this would call your RAG API)
    // setTimeout(() => {
    //   const aiResponse: Message = {
    //     id: (Date.now() + 1).toString(),
    //     content:
    //       "Based on the video transcript, I found relevant information about your query. [This would be the actual RAG response from your embeddings]",
    //     sender: "assistant",
    //     timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    //   }

    //   setMessages((prev) => ({
    //     ...prev,
    //     [selectedVideo]: [...(prev[selectedVideo] || []), aiResponse],
    //   }))
    // }, 1000)
  }

  const handleAddVideo = (videoUrl: string) => {
    const videoId = extractVideoId(videoUrl)
    if (!videoId) return

    const newConversation: VideoConversation = {
      id: Date.now().toString(),
      title: `Video ${videoId}`,
      description: "Processing transcript...",
      videoId,
    }

    // setConversations((prev) => [newConversation, ...prev])
    setMessages((prev) => ({ ...prev, [newConversation.id]: [] }))
  }

  const extractVideoId = (url: string): string | null => {
    // Simple YouTube URL parsing (extend for other platforms)
    const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/)
    return match ? match[1] : url // Return the URL as-is if not a YouTube URL
  }

  // const selectedTranscriptData = transcripts.find((t) => t.id === selectedTranscript)
  // const currentMessages = selectedTranscript ? messages[selectedTranscript] || [] : []

  const handleSelectVideo = async (video: VideoData) => {
    setSelectedVideo(video)
    const messages = await getMessages(video.video_id)
    setMessages(messages)
    console.log(messages)
    // setMessages(messages[video.id] || [])
  }

  return (
    <div className="flex h-full bg-background">
      {/* Left Pane - Video List */}
      <div className="w-80 border-r border-border flex-shrink-0">
        <VideoList
          videos={videos}
          selectedVideo={selectedVideo}
          onSelectVideo={handleSelectVideo}
          onAddVideo={handleAddVideo}
        />
      </div>

      {/* Right Pane - Chat Area */}
      <div className="flex-1 flex flex-col">
        <ChatArea
          selectedVideo={selectedVideo}
          // conversation={selectedTranscriptData}
          messages={messages}
          onSendMessage={handleSendMessage}
        />
      </div>
    </div>
  )
}
