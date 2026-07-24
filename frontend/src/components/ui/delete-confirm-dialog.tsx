type DeleteConfirmDialogProps = {
  busy?: boolean;
  confirmLabel?: string;
  description: string;
  onCancel: () => void;
  onConfirm: () => void | Promise<void>;
  subject: string;
  title: string;
};

export function DeleteConfirmDialog({
  busy = false,
  confirmLabel = "删除",
  description,
  onCancel,
  onConfirm,
  subject,
  title,
}: DeleteConfirmDialogProps) {
  return (
    <div className="delete-dialog-backdrop" role="presentation">
      <section aria-labelledby="delete-dialog-title" aria-modal="true" className="delete-dialog" role="dialog">
        <h2 id="delete-dialog-title">{title}</h2>
        <p className="delete-dialog-copy">
          <strong>{subject}</strong>
        </p>
        <p className="delete-dialog-muted">{description}</p>
        <div className="delete-dialog-actions">
          <button className="delete-dialog-cancel" disabled={busy} onClick={onCancel} type="button">
            取消
          </button>
          <button className="delete-dialog-danger" disabled={busy} onClick={onConfirm} type="button">
            {busy ? "处理中" : confirmLabel}
          </button>
        </div>
      </section>
    </div>
  );
}
