// The Assistant page: a conversation about the portfolio.

import { useState } from 'react'

import Alert from '../components/Alert'
import Button from '../components/Button'
import Card from '../components/Card'
import ChatComposer from '../components/ChatComposer'
import ChatMessages from '../components/ChatMessages'
import PageLayout from '../components/PageLayout'
import SuggestedQuestions from '../components/SuggestedQuestions'
import { useChat } from '../hooks/useChat'
import { MUTED_TEXT } from '../lib/styles'

function AssistantPage() {
  const { messages, error, send, startOver } = useChat()
  const [draft, setDraft] = useState('')
  const hasMessages = messages.length > 0

  return (
    <PageLayout title="Assistant">
      <Card
        title="Conversation"
        aside={
          hasMessages && (
            <Button variant="secondary" onClick={startOver}>
              New conversation
            </Button>
          )
        }
      >
        <div className="space-y-4">
          {hasMessages ? (
            <ChatMessages messages={messages} />
          ) : (
            <SuggestedQuestions onChoose={setDraft} />
          )}
          {error !== null && <Alert variant="warning">{error}</Alert>}
          <ChatComposer text={draft} onChange={setDraft} onSend={send} />
          <p className={MUTED_TEXT}>
            Answers are written by an AI model. Every figure comes from the same data as the other
            pages, where it can be checked.
          </p>
        </div>
      </Card>
    </PageLayout>
  )
}

export default AssistantPage
