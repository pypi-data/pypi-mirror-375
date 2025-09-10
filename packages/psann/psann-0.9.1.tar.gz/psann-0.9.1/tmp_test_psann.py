from pathlib import Path
import sys
sys.path.insert(0, str(Path('.','src')))
from psann import PSANNLanguageModel, LMConfig, SimpleWordTokenizer, SineTokenEmbedder

corpus = [
    "the quick brown fox jumps over the lazy dog",
    "the quick blue hare sprints under the bright sun",
    "curious cats nap over warm rugs",
    "dogs bark and foxes dash swiftly",
]

tok = SimpleWordTokenizer(lowercase=True)
emb = SineTokenEmbedder(embedding_dim=8, trainable=True)
cfg = LMConfig(embedding_dim=8, extras_dim=4, episode_length=8, batch_episodes=2, random_state=0)
lm = PSANNLanguageModel(tokenizer=tok, embedder=emb, lm_cfg=cfg, hidden_layers=1, hidden_width=16, activation_type='psann')

lm.fit(corpus, epochs=1, lr=1e-3, verbose=0, ppx_every=1)
print('OK: trained 1 epoch')
print('Predict:', lm.predict('the quick'))
print('Generate:', lm.generate('the', max_tokens=3))
