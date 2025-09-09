# Pytornis

Pytornis es una biblioteca de **cómputo industrial para IA y Deep Learning** completamente autocontenida, inspirada en PyTorch y NumPy. Su diseño permite entrenar modelos de manera **real, industrial y distribuida**, sin dependencias externas (solo C++ embebido con compilación automática opcional con clang/nvcc).

## Características Principales

- Tensores multidimensionales en CPU y GPU (FP16, FP32, INT8).
- Kernels optimizados propios para cálculos lineales y convoluciones.
- AutoGrad: diferenciación automática completa.
- Capas y módulos: Linear, Conv2D, Pooling, BatchNorm, Dropout.
- Optimizadores nativos: SGD, Adam, RMSProp, Lion, con búsqueda automática de hiperparámetros.
- Entrenamiento distribuido y pipelines asincrónicos.
- Vectorización avanzada y tokenización nativa (soporte GPT/CPT).
- Tensores de audio/video para entrenamiento de modelos multimodales.
- Precisión mixta y autotuning dinámico de kernels.
- DataLoader con prefetching y mini-batches.
- Propio sistema ONNX-like para importar/exportar modelos.
- Autocontenido: no requiere PyTorch, NumPy, TensorFlow ni CUDNN.

## Instalación

```bash
pip install pytornis
