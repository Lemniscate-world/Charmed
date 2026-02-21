# Project Aladin: Probabilistic Transformer Implementation

This plan follows the **Pedagogical Protocol**. We will build a Transformer-based model to predict time series distributions in the `Aladin` repository.

## Technical Roadmap

### Phase 1: Conceptual Briefings
We will cover the "Why" and "How" of:
1. **Synthetic Data**: Why it's the only way to verify uncertainty. (DONE)
2. **Transformers & Attention**: Why Attention is better than RNNs for long-term dependencies. (IN PROGRESS)
3. **Gaussian Heads**: How to output a distribution instead of a point.
4. **NLL Loss**: The math of maximum likelihood estimation.

### Phase 2: Implementation (The 12 Steps)
1.  **Générateur Synthétique** : Créer une fonction Sinus + Bruit Gaussien.
2.  **Dataset PyTorch** : Gérer les fenêtres glissantes (Sliding Windows).
3.  **Encodage Positionnel** : Aider le Transformer à comprendre l'ordre du temps.
4.  **Cœur du Transformer** : Construire l'encodeur (Multi-Head Attention).
5.  **Tête Probabiliste** : Couche de sortie pour Moyenne (mu) et Log-Variance.
6.  **Intégration du Modèle** : Assembler le tout dans `ProbabilisticTransformer`.
7.  **Fonction de Perte (NLL)** : Implémenter la Negative Log-Likelihood.
8.  **Boucle d'Entraînement** : Optimisation avec Adam.
9.  **Pipeline de Validation** : Tester sur des données non vues.
10. **Entraînement Baseline** : Lancer le premier apprentissage.
11. **Visualisation** : Tracer la moyenne +/- l'incertitude.
12. **Debug NeuralDBG** : Vérifier la santé des gradients avec l'outil de causalité.

## Verification Plan
1. **Gaussian Test**: Verify that the model can recover the known noise level of synthetic data.
2. **Visual Check**: Plot predicted mean +/- standard deviation.
3. **NeuralDBG**: Monitor for exploding gradients in the LogVar output.
