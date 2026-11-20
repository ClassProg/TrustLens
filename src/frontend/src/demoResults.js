export const demoResults = {
  prediction: {
    label: 'GLAUCOMA DETECTED',
    model: 'ResNet50',
    confidence: '100.0%',
  },
  explanations: [
    { label: 'Integrated Gradients', image: 'v0075-integrated-gradients.png' },
    { label: 'Grad-CAM', image: 'v0075-grad-cam.png' },
    { label: 'LIME', image: 'v0075-lime.png' },
  ],
  evaluationMethods: ['Grad-CAM', 'Integrated Gradients', 'LIME'],
  evaluation: [
    { metric: 'Faithfulness', scores: ['0.86', '0.82', '0.74'] },
    { metric: 'Robustness', scores: ['0.91', '0.87', '0.79'] },
    { metric: 'Localization', scores: ['0.89', '0.84', '0.76'] },
  ],
};
