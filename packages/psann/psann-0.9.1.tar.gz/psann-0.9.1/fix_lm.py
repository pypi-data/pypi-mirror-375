import re
from pathlib import Path
p = Path('src/psann/lm.py')
s = p.read_text(encoding='utf-8')
replacement = '''@torch.no_grad()
    def _batch_perplexity(self, pred: torch.Tensor, next_ids: torch.Tensor) -> float:
        """Compute perplexity using cosine-sim softmax over vocab embeddings.

        pred: (B,T,D), next_ids: (B,T)
        """
        D = pred.shape[-1]
        # Rebuild table if embedder is trainable so it reflects latest params
        try:
            if any(p.requires_grad for p in self.embedder.parameters()):
                self.embedder._rebuild_table()
        except Exception:
            pass
        table = self.embedder.embedding_matrix()  # (V,D)
        if table.numel() == 0:
            return float('nan')
        # Normalize
        tn = table / (table.norm(p=2, dim=1, keepdim=True) + 1e-8)
        y = pred.reshape(-1, D)
        yn = y / (y.norm(p=2, dim=1, keepdim=True) + 1e-8)
        logits = torch.matmul(yn, tn.T) / max(1e-6, float(self.cfg.ppx_temperature))  # (B*T, V)
        # cross-entropy to true next token ids
        tgt = next_ids.reshape(-1).to(device=logits.device, dtype=torch.long)
        log_probs = logits - torch.logsumexp(logits, dim=1, keepdim=True)
        nll = -log_probs[torch.arange(logits.shape[0]), tgt].mean()
        ppl = torch.exp(nll).item()
        return float(ppl)

    '''
s2, n = re.subn(r'@torch\.no_grad\(\)\s*def _batch_perplexity\(.*?\):[\s\S]*?return float\(ppl\)\s*', replacement, s, flags=re.S)
s = s2
s = s.replace('\\n', '\n')
p.write_text(s, encoding='utf-8')
print('patched', n)
