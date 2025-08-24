import type React from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Send, ExternalLink, FileText } from "lucide-react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { useState, useRef, useEffect } from "react"
import { cn } from "@/lib/utils"
import type { VideoData, Message } from "@/types/types"

interface ChatAreaProps {
  selectedVideo: VideoData | null
  messages: Message[]
  onSendMessage: (content: string) => void
}

export function ChatArea({ selectedVideo, messages, onSendMessage }: ChatAreaProps) {
  const [newMessage, setNewMessage] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false)
  const [convoSummary, setConvoSummary] = useState("")
  const [isSummaryModalOpen, setIsSummaryModalOpen] = useState(false)
  const [isConvoSummaryModalOpen, setIsConvoSummaryModalOpen] = useState(false)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = () => {
    if (newMessage.trim()) {
      console.log("SENDING MESSAGE:", newMessage)
      onSendMessage(newMessage.trim())
      setNewMessage("")
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleGenerateSummary = async () => {
    setIsGeneratingSummary(true)
    setIsConvoSummaryModalOpen(true)

    setTimeout(() => {
      // const conversationText = messages.map((m) => `${m.sender}: ${m.content}`).join("\n")
      // setSummary(
      //   `Summary of conversation about "${conversation?.title}":\n\nThis conversation covered key topics from the video transcript. The user asked ${messages.filter((m) => m.sender === "user").length} questions and received detailed responses about the video content. Main discussion points included analysis of the video's core themes and specific details requested by the user.`,
      // )
      setIsGeneratingSummary(false)
    }, 2000)
  }

  if (!selectedVideo) {
    return (
      <div className="flex-1 flex items-center justify-center text-muted-foreground ml-1">
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
        <div className="flex items-center gap-2">
          <Dialog open={isSummaryModalOpen} onOpenChange={setIsSummaryModalOpen}>
            <DialogTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                title="View transcript summary"
                // onClick={handleGenerateSummary}
                className="!bg-transparent hover:!bg-accent focus:!outline-none !border-0"
              >
                {/* h-6 w-6 p-0 !bg-transparent hover:!bg-destructive/10 hover:!text-destructive !border-0 */}
                <FileText className="h-4 w-4" />
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto" aria-describedby={undefined}>
              <DialogHeader>
                <DialogTitle>Video Summary</DialogTitle>
              </DialogHeader>
                <div className="mt-4">
                  {/* {isGeneratingSummary ? (
                    <div className="flex items-center justify-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                      <span className="ml-3 text-muted-foreground">Generating summary...</span>
                    </div>
                  ) : ( */}
                    <div className="prose prose-sm max-w-none">
                      <pre className="whitespace-pre-wrap text-sm leading-relaxed">{selectedVideo.summary}</pre>
                    </div>
                  {/* )} */}
                </div>
              </DialogContent>
            </Dialog>
          </div>
        <div className="flex-1 min-w-0 flex flex-col items-start ml-2">
          <h3 className="font-medium truncate">{selectedVideo.title}</h3>
          {selectedVideo.description && (
            <p className="text-sm text-muted-foreground truncate">{selectedVideo.description}</p>
          )}
          <p className="text-xs font-mono text-muted-foreground">ID: {selectedVideo.video_id}
            <a
            href={`https://www.youtube.com/watch?v=${selectedVideo.video_id}`}
            target="_blank"
            rel="noopener noreferrer"
            // className="!bg-transparent hover:!bg-accent focus:!outline-none focus:bg-accent !border-0 w-1 h-1"
            >
          <Button
            variant="ghost"
            size="icon"
            title="Open video"
            className="!bg-transparent hover:!bg-accent focus:!outline-none focus:bg-accent !border-0 w-1 h-1"
            >
            <ExternalLink className="h-4 w-4" />
          </Button>
          </a>
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Dialog open={isConvoSummaryModalOpen} onOpenChange={setIsConvoSummaryModalOpen}>
            <DialogTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                title="Generate conversation summary"
                onClick={handleGenerateSummary}
                disabled={messages.length === 0}
                className="!bg-transparent hover:!bg-accent focus:!outline-none focus:!bg-accent !border-0"
              >
                <FileText className="h-4 w-4" />
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto" aria-describedby={undefined}>
              <DialogHeader>
                <DialogTitle>Conversation Summary</DialogTitle>
              </DialogHeader>
              <div className="mt-4">
                {isGeneratingSummary ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                    <span className="ml-3 text-muted-foreground">Generating summary...</span>
                  </div>
                ) : (
                  <div className="prose prose-sm max-w-none">
                    <pre className="whitespace-pre-wrap text-sm leading-relaxed">{convoSummary}</pre>
                  </div>
                )}
              </div>
            </DialogContent>
          </Dialog>

          {/* <Button
            variant="ghost"
            size="icon"
            title="Open video"
            className="!bg-transparent hover:bg-accent focus:outline-none focus:bg-accent border-0"
          >
            <ExternalLink className="h-4 w-4" />
          </Button> */}
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 max-h-96">
        {messages.length === 0 ? "No messages yet. Start the conversation!" :
        messages.map((message) => (
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
              <span className="text-xs text-muted-foreground">{message.created_at === "temp" ? "Sending..." : message.created_at}</span>
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
            onKeyDown={handleKeyDown}
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
