// Example questions shown on an empty chat. Choosing one puts it in the question box.

import { SUGGESTED_QUESTIONS } from '../lib/chat'
import { MUTED_TEXT } from '../lib/styles'
import Button from './Button'

function SuggestedQuestions({ onChoose }: { onChoose: (question: string) => void }) {
  return (
    <div className="space-y-3">
      <p className={MUTED_TEXT}>Ask a question about the portfolio, or start with one of these.</p>
      <ul className="flex flex-wrap gap-2">
        {SUGGESTED_QUESTIONS.map((question) => (
          <li key={question}>
            <Button variant="secondary" onClick={() => onChoose(question)}>
              {question}
            </Button>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default SuggestedQuestions
