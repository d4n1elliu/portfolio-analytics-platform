// The Assistant page: the user's conversations about the portfolio, and the one that is open.

import { useState } from 'react'

import { deleteConversation, listConversations } from '../api/chat'
import { messageFrom } from '../api/client'
import Alert from '../components/Alert'
import Card from '../components/Card'
import ChatComposer from '../components/ChatComposer'
import ChatMessages from '../components/ChatMessages'
import ConversationList from '../components/ConversationList'
import PageLayout from '../components/PageLayout'
import SuggestedQuestions from '../components/SuggestedQuestions'
import { useApiQuery } from '../hooks/useApiQuery'
import { useChat } from '../hooks/useChat'
import { MUTED_TEXT } from '../lib/styles'

const COULD_NOT_DELETE = 'The conversation could not be deleted.'

function AssistantPage() {
  const { state: conversations, reload } = useApiQuery(listConversations, {
    keepPreviousData: true,
  })
  const chat = useChat({ onConversationUsed: reload })
  const [draft, setDraft] = useState('')
  const [deleteError, setDeleteError] = useState<string | null>(null)

  async function handleDelete(id: string) {
    setDeleteError(null)
    try {
      await deleteConversation(id)
      if (id === chat.conversationId) chat.startOver()
    } catch (thrown) {
      setDeleteError(messageFrom(thrown, COULD_NOT_DELETE))
    }
    reload()
  }

  return (
    <PageLayout title="Assistant">
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[18rem_1fr]">
        <Card title="Conversations">
          {deleteError !== null && <Alert variant="error">{deleteError}</Alert>}
          <ConversationList
            state={conversations}
            openId={chat.conversationId}
            onRetry={reload}
            onOpen={chat.open}
            onDelete={handleDelete}
            onStartNew={chat.startOver}
          />
        </Card>
        <Card title="Conversation">
          <div className="space-y-4">
            {chat.messages.length > 0 ? (
              <ChatMessages messages={chat.messages} />
            ) : (
              <SuggestedQuestions onChoose={setDraft} />
            )}
            {chat.error !== null && <Alert variant="error">{chat.error}</Alert>}
            <ChatComposer
              text={draft}
              onChange={setDraft}
              onSend={chat.send}
              busy={chat.answering}
            />
            <p className={MUTED_TEXT}>
              Answers are written by an AI model. Every figure comes from the same data as the other
              pages, where it can be checked.
            </p>
          </div>
        </Card>
      </div>
    </PageLayout>
  )
}

export default AssistantPage
