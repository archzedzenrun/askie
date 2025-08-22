import { useState, useEffect } from "react"
import { VideoList } from "./video-list"
import { ChatArea } from "./chat-area"
import { getVideos, getMessages, sendMessage, newVideo } from "@/services/videosService"
import type { VideoData, Message, NewMessageData, NewVideoData } from "@/types/types"

export function ChatLayout() {
  const [videos, setVideos] = useState<VideoData[]>([])
  const [messages, setMessages] = useState<Message[]>([])
  const [selectedVideo, setSelectedVideo] = useState<VideoData | null>(null)

  useEffect(() => {
    const fetchVideos = async () => {
      try {
        const request = await getVideos()
        const videoData = request.data
        setVideos(videoData)
      } catch (error) {
        console.error("Error fetching Videos:", error)
      }
     }
     
    fetchVideos()
  }, [])

  const handleSendMessage = async (content: string) => {
    if (!selectedVideo) return

    const tempId = Date.now().toString()
    setMessages(prev => [...prev, { id: tempId, role: "user", content: content, video_id: selectedVideo.video_id, created_at: "temp" }]);

    const data: NewMessageData = { "video_id": selectedVideo.video_id,
                                   "query": content }
    try {
      const res = await sendMessage(data)
      console.log("RESPONSE:", res)
      const withoutTemp = messages.filter(msg => msg.id !== tempId)
      setMessages([...withoutTemp, res.user, res.assistant])
      console.log("MESSAGES:", messages)
    } catch (error) {
      console.error("Error sending message:", error)
    }
  }

  const handleAddVideo = async (url: string, title: string, description: string) => {
    const videoId = extractVideoId(url)
    if (!videoId) {
      console.error("Invalid video URL")
      return
    }

    const videoData: NewVideoData = {
      video_id: videoId,
      title: title,
      description: description,
    }

    try {
      const response = await newVideo(videoData)
      console.log("New video added:", response)
      setVideos(prev => [...prev, response.video_data])
      // setSelectedVideo(response)

      // Fetch messages for the newly added video
      // const messages = await getMessages(response.video_id)
      // setMessages(messages)
    } catch (error) {
      console.error("Error adding new video:", error)
    }
    // if (!videoId) return

    // const newConversation: VideoConversation = {
    //   id: Date.now().toString(),
    //   title: `Video ${videoId}`,
    //   description: "Processing transcript...",
    //   videoId,
    // }

    // // setConversations((prev) => [newConversation, ...prev])
    // setMessages((prev) => ({ ...prev, [newConversation.id]: [] }))
  }

  const extractVideoId = (url: string): string | null => {
    // Simple YouTube URL parsing (extend for other platforms)
    const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/)
    return match ? match[1] : url // Return the URL as-is if not a YouTube URL
  }

  const handleSelectVideo = async (video: VideoData) => {
    try {
      setSelectedVideo(video)
      const messages = await getMessages(video.video_id)
      setMessages(messages)
    } catch (error) {
      console.error("Error fetching messages:", error)
    }
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
          messages={messages}
          onSendMessage={handleSendMessage}
        />
      </div>
    </div>
  )
}
