import Alert from './Alert'
import Button from './Button'

interface LoadErrorProps {
  message: string
  onRetry: () => void
  className?: string
}

function LoadError({ message, onRetry, className = '' }: LoadErrorProps) {
  return (
    <div className={`space-y-3 ${className}`}>
      <Alert variant="error">{message}</Alert>
      <Button variant="secondary" onClick={onRetry}>
        Try again
      </Button>
    </div>
  )
}

export default LoadError
