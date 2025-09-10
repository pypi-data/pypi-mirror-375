from pathlib import Path
p = Path('src/psann/lm.py')
s = p.read_text(encoding='utf-8')
s = s.replace(
    '            # Nearest neighbor decoding\n            table = self.embedder.embedding_matrix()',
    '            # Nearest neighbor decoding\n            # Ensure table is up-to-date if embedder is trainable\n            try:\n                if any(p.requires_grad for p in self.embedder.parameters()):\n                    self.embedder._rebuild_table()\n            except Exception:\n                pass\n            table = self.embedder.embedding_matrix()'
)
p.write_text(s, encoding='utf-8')
print('OK')
