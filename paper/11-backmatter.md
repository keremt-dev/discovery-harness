# Acknowledgements

The problem-selection methodology of the broader discovery programme
behind this paper was motivated by the published work of G. Yazgı
Tütüncü and Cihangir Özkut on reliability design optimization; we
thank them for that inspiration. We also thank Dan Gordon for three
decades of curation of the covering repository, without which the
stagnant-frontier experimental setting of this paper would not exist.

# Reproducibility and Artifacts

All code, certificates, frozen protocols, and raw logs are released
at [REPO-URL]: the problem-agnostic harness and covering plugin (MIT
license), solution certificates with a standalone stdlib verifier
(CC-BY 4.0), the pre-registered benchmark protocol with its results
table, the controlled-experiment slice logs, and the contamination
probe transcripts. Every tie claimed in this paper can be re-verified
in minutes with `python verify_cover.py v k t solution.txt`, which
shares no code with the harness. The evolution runs used OpenEvolve
0.3.2 with configuration files included in the repository; model
access went through a local OpenAI-compatible proxy, and we document
the serving-stack behaviors (reasoning-mode payload overrides,
ensemble-seeding pathology) that affect reproduction.
