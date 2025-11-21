# 🎯 Quick Reference - New Features

## 🚀 Quick Start
```bash
./start.sh  # Starts all services
```

---

## 🔗 API Endpoints Cheatsheet

### Real-Time Collaboration
```bash
# WebSocket
ws://localhost:8000/ws/canvas/<project_id>/

# REST APIs
GET  /api/projects/collaboration/sessions/active/?project_id=1
GET  /api/projects/collaboration/edits/recent/?project_id=1&limit=50
```

### Comments
```bash
# List comments
GET  /api/projects/comments/?project_id=1

# Create comment
POST /api/projects/comments/
{
  "project": 1,
  "content": "Great design!",
  "anchor_position": {"x": 100, "y": 200}
}

# Resolve comment
POST /api/projects/comments/123/resolve/
{"is_resolved": true}

# Get unresolved
GET  /api/projects/comments/unresolved/?project_id=1
```

### Reviews
```bash
# Request review
POST /api/projects/reviews/request_review/
{
  "project_id": 1,
  "reviewer_id": 2,
  "message": "Please review"
}

# Submit review
POST /api/projects/reviews/123/submit/
{
  "status": "approved",
  "summary": "Looks great!",
  "overall_rating": 9
}

# Get pending reviews
GET  /api/projects/reviews/pending/
```

### AI - Generate Variants
```bash
POST /api/ai/enhanced/generate_variants/
{
  "prompt": "Modern tech landing page",
  "design_type": "ui_ux",
  "num_variants": 3
}
```

### AI - Auto-Responsive
```bash
POST /api/ai/enhanced/auto_layout/
{
  "project_id": 1,
  "target_sizes": [
    {"width": 1920, "height": 1080, "name": "desktop"},
    {"width": 768, "height": 1024, "name": "tablet"}
  ]
}
```

### AI - Improvements
```bash
POST /api/ai/enhanced/suggest_improvements/
{
  "project_id": 1,
  "focus_areas": ["color", "typography"]
}
```

### AI - Accessibility
```bash
POST /api/ai/enhanced/check_accessibility/
{"project_id": 1}
```

### AI - Brand Assets
```bash
POST /api/ai/enhanced/generate_brand_assets/
{
  "brand_description": "Eco-friendly tech startup",
  "asset_types": ["logo", "color_palette", "typography"]
}
```

### Templates
```bash
# Browse templates
GET  /api/projects/enhanced-templates/?category=social_media

# Popular templates
GET  /api/projects/enhanced-templates/popular/?limit=10

# Create from project
POST /api/projects/enhanced-templates/create_from_project/
{
  "project_id": 1,
  "name": "My Template",
  "category": "social_media",
  "is_public": true
}

# Use template
POST /api/projects/enhanced-templates/123/use/
{"name": "New Project"}
```

---

## 💻 Frontend Usage

### Collaborative Canvas Hook
```typescript
import { useCollaborativeCanvas } from '@/hooks/useCollaborativeCanvas';

const { 
  isConnected, 
  activeUsers, 
  updateElement,
  sendCursorPosition 
} = useCollaborativeCanvas(projectId, token);

// Update element
updateElement('elem-1', { color: '#FF0000' }, { color: '#000000' });

// Send cursor
sendCursorPosition(100, 200);
```

### AI Variants Component
```typescript
import { AIVariantsGenerator } from '@/components/ai/AIVariantsGenerator';

<AIVariantsGenerator 
  onVariantSelect={(variant) => {
    // Apply variant to canvas
    console.log('Selected variant:', variant);
  }}
/>
```

### Comments Panel
```typescript
import { CommentsPanel } from '@/components/collaboration/CommentsPanel';

<CommentsPanel 
  projectId={projectId}
  onCommentClick={(comment) => {
    // Jump to comment location on canvas
    if (comment.anchor_position) {
      canvas.panTo(comment.anchor_position);
    }
  }}
/>
```

---

## 🐍 Python Service Usage

### Version Control
```python
from projects.version_control_service import VersionControlService

# Create branch
branch = VersionControlService.create_branch(
    project=project,
    name='feature/new-layout',
    user=request.user
)

# Create commit
commit = VersionControlService.create_commit(
    branch=branch,
    project=project,
    user=request.user,
    message='Updated hero section',
    design_data={'elements': [...]}
)

# Merge branches
merge_commit = VersionControlService.merge_branches(
    merge_request=mr,
    user=request.user
)
```

### Search Service
```python
from projects.semantic_search_service import SemanticSearchService

# Search projects
results = SemanticSearchService.search_projects(
    query='landing page',
    user=request.user,
    filters={'project_type': 'ui_ux'}
)

# Search by color
results = SemanticSearchService.search_by_color(
    hex_color='#FF5733',
    tolerance=30
)
```

### Export Service
```python
from projects.enhanced_export_service import EnhancedExportService

# Export to SVG
svg = EnhancedExportService.export_to_svg(
    design_data={'elements': [...]},
    width=1920,
    height=1080
)

# Export to Figma
figma_json = EnhancedExportService.export_to_figma_json(
    design_data={'elements': [...]},
    width=1920,
    height=1080
)
```

---

## 🔧 Database Commands

```bash
# Create migrations
python manage.py makemigrations projects

# Apply migrations
python manage.py migrate

# Shell access
python manage.py shell

# Create test data
python manage.py shell
>>> from projects.models import Project
>>> from django.contrib.auth.models import User
>>> user = User.objects.first()
>>> project = Project.objects.create(
...     user=user,
...     name="Test Project",
...     project_type="graphic"
... )
```

---

## 🧪 Testing Commands

```bash
# Test WebSocket
cd backend
python manage.py test projects.tests.test_collaboration

# Test AI services
python manage.py test ai_services.tests.test_enhanced_ai

# Test version control
python manage.py test projects.tests.test_version_control

# Run all tests
python manage.py test
```

---

## 🐛 Troubleshooting

### WebSocket not connecting
```bash
# Check Redis
redis-cli ping  # Should return PONG

# Check Django Channels
python manage.py shell
>>> import channels
>>> print(channels.__version__)
```

### AI requests failing
```bash
# Check API keys
echo $OPENAI_API_KEY
echo $GROQ_API_KEY

# Test API
curl -X POST http://localhost:8000/api/ai/enhanced/generate_variants/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"prompt": "test", "num_variants": 1}'
```

### Migrations error
```bash
# Reset migrations (dev only!)
find backend -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate
```

---

## 📊 Monitoring

### Check logs
```bash
# Backend logs
tail -f backend/logs/django.log
tail -f backend/logs/ai.log
tail -f backend/logs/celery.log

# All logs
tail -f backend/logs/*.log
```

### Check services
```bash
# Django
curl http://localhost:8000/api/docs/

# Redis
redis-cli ping

# Celery
celery -A backend inspect active
```

---

## 🎨 Feature Status

- ✅ Real-time collaboration
- ✅ Comments & reviews
- ✅ AI variants generation
- ✅ Auto-responsive layouts
- ✅ Accessibility checker
- ✅ Version control
- ✅ Export (SVG, PDF, Figma)
- ✅ Template library
- ✅ Semantic search

---

## 📚 Documentation Links

- **Full Guide:** `NEW_FEATURES_GUIDE.md`
- **Summary:** `IMPLEMENTATION_SUMMARY.md`
- **API Docs:** http://localhost:8000/api/docs/
- **README:** `README_V2.md`

---

## 🆘 Quick Help

```bash
# Start all services
./start.sh

# Stop all services (if using tmux)
tmux kill-session -t aidesign

# View running services
tmux attach -t aidesign

# Check what's running
lsof -i :8000  # Django
lsof -i :3000  # Frontend
lsof -i :6379  # Redis
```

---

**Need more help? Check the full documentation!** 📖
