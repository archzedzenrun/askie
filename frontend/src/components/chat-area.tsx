import type React from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Send, ExternalLink } from "lucide-react"
import { useState, useRef, useEffect } from "react"
import { cn } from "@/lib/utils"
import type { Message } from "@/types/types"
import type { VideoData } from "@/types/types"

interface ChatAreaProps {
  selectedVideo: VideoData | null
  messages: Message[]
  onSendMessage: (content: string) => void
}

export function ChatArea({ selectedVideo, messages, onSendMessage }: ChatAreaProps) {
  const [newMessage, setNewMessage] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = () => {
    if (newMessage.trim()) {
      onSendMessage(newMessage.trim())
      setNewMessage("")
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  if (!selectedVideo) {
    return (
      <div className="flex-1 flex items-center justify-center text-muted-foreground">
        <div className="text-center">
          <h3 className="text-lg font-medium mb-2">No video selected</h3>
          <p>Choose a video from the sidebar to start asking questions</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Chat Header */}
      <div className="flex justify-between p-4 border-b border-border">
        <div className="flex-1 min-w-0">
          <h3 className="font-medium truncate">{selectedVideo.title}</h3>
          {selectedVideo.description && (
            <p className="text-sm text-muted-foreground truncate">{selectedVideo.description}</p>
          )}
          <p className="text-xs font-mono text-muted-foreground">ID: {selectedVideo.video_id}</p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            title="Open video"
            className="!bg-transparent hover:bg-accent focus:outline-none focus:bg-accent border-0"
          >
            <ExternalLink className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 max-h-96">
        {messages.map((message) => (
          <div
            key={message.id}
            className={cn("flex gap-3 max-w-[85%]", message.role === "user" ? "ml-auto flex-row-reverse" : "")}
          >
            <div className={cn("flex flex-col gap-1", message.role === "user" ? "items-end" : "items-start")}>
              <div
                className={cn(
                  "rounded-lg px-4 py-3 max-w-full break-words",
                  message.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted border",
                )}
              >
                <p className="text-sm leading-relaxed">{message.content}</p>
              </div>
              <span className="text-xs text-muted-foreground">{message.created_at}</span>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <div className="p-4 border-t border-border">
        <div className="flex gap-2">
          <Input
            placeholder="Ask a question about this video..."
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            className="flex-1"
          />
          <Button 
            onClick={handleSend} 
            disabled={!newMessage.trim()}
            className={cn(
              "!bg-blue-600 hover:!bg-blue-700 !text-white",
              "disabled:!bg-gray-300 disabled:!text-gray-500 disabled:!cursor-not-allowed",
              "!transition-colors",
            )}
            >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}
