type ComposerSendButtonProps = {
  busy: boolean;
  onStop?: () => void;
};

export function ComposerSendButton({ busy, onStop }: ComposerSendButtonProps) {
  if (busy) {
    return (
      <button
        aria-label="停止生成"
        className="primary-button composer-send composer-stop"
        title="停止生成"
        type="button"
        onClick={onStop}
      >
        <svg aria-hidden="true" className="composer-send-icon spinner" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="10" />
        </svg>
      </button>
    );
  }

  return (
    <button
      aria-label="发送"
      className="primary-button composer-send"
      title="发送"
      type="submit"
    >
      <svg aria-hidden="true" className="composer-send-icon" viewBox="0 0 24 24">
        <path d="M12 5v14M6.5 10.5 12 5l5.5 5.5" />
      </svg>
    </button>
  );
}
