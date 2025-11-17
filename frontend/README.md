# Frontend - AI Design Tool

The frontend application for the AI-Powered Design Tool, a comprehensive design platform combining Graphic Design (Canva-like), UI/UX Design (Figma-like), and AI-powered Logo Generation.

## 🚀 Features

- **Canvas Editor**: Drag-and-drop design editor powered by Fabric.js
- **AI Integration**: Text-to-design generation using GPT-4
- **Component Library**: Pre-built UI components with Shadcn UI
- **Responsive Design**: Mobile-first responsive layouts
- **Real-time Collaboration**: Live editing with other users
- **Export Options**: PNG, SVG, PDF, and Figma JSON export

## 🛠️ Tech Stack

- **Framework**: Next.js 16 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Shadcn/ui
- **Canvas**: Fabric.js
- **State Management**: TanStack Query + Zustand
- **API**: RESTful API with Django backend

## 🚦 Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Set up environment variables**

   Create a `.env.local` file in the frontend directory:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
   ```

4. **Run development server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

5. **Open your browser**

   Navigate to [http://localhost:3000](http://localhost:3000)

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/               # Next.js app router pages
│   ├── components/        # Reusable UI components
│   │   ├── canvas/        # Canvas editor components
│   │   ├── ui/            # Shadcn UI components
│   │   └── ...
│   ├── lib/               # Utilities and API clients
│   ├── hooks/             # Custom React hooks
│   └── constants/         # App constants
├── public/                # Static assets
└── ...
```

## 🔧 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## 🌐 API Integration

The frontend communicates with the Django backend API. Make sure the backend is running on the configured API URL.

## 📚 Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Fabric.js Documentation](https://fabricjs.com/)
- [Shadcn/ui Documentation](https://ui.shadcn.com/)

## 🤝 Contributing

1. Follow the existing code style
2. Write tests for new features
3. Update documentation as needed
