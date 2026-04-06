# SonicLab AI: Advanced Music Genre Classifier 🎵🤖

**SonicLab** is a premium audio analysis platform that uses an Artificial Neural Network (ANN) to classify music samples into 10 distinct genres with high precision. Featuring a high-end interface with an interactive vinyl experience, this project combines digital signal processing (DSP) with modern deep learning.

## ✨ Key Features
- **Neural Architecture**: Deep MLP with 55 feature vectors (MFCCs, Chroma, Spectral Centroid, etc.).
- **Interactive UI**: A premium dark-mode studio interface featuring a rotating vinyl player and dynamic animations (Framer Motion).
- **Real-time Analysis**: Instant genre detection with confidence scoring.
- **Robust Feature Engineering**: Advanced signal extraction using `librosa`.

## 🛠️ Tech Stack
- **Backend**: Python, FastAPI, PyTorch, Librosa, Scikit-learn.
- **Frontend**: Next.js 15, React 19, Tailwind CSS, Framer Motion, Lucide Icons.

## 🚀 Getting Started

### 1. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the pre-processing and training (Optional if `music_ann.pth` exists):
   ```bash
   python preprocess.py
   python train.py
   ```
5. Start the server:
   ```bash
   python -m uvicorn main:app --reload --port 8000
   ```

### 2. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## 📊 Model Performance
The system achieves a **76.00% validation accuracy** on the GTZAN dataset, utilizing a refined feature set that captures both spectral characteristics and temporal dynamics.

## ⚖️ Credits
Developed as a Professional Computer Engineering Project - **Rabia and Deniz's Professional Studio**.
