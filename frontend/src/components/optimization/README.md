# Optimization Components

## OptimizationProgressBar

Enhanced progress bar component for optimization jobs with real-time updates.

### Features

- **Visual Progress Indicator**: Gradient-filled progress bar with percentage overlay
- **Status Icons**: Visual indicators for different job states (running, completed, failed, pending)
- **Animated Effects**: Shimmer animation for running jobs, pulse effect for active processing
- **Time Tracking**:
  - Elapsed time since job start
  - Estimated time remaining until completion
- **Iteration Count**: Current iteration number display
- **Responsive Design**: Adapts to container width with proper spacing

### Usage

```tsx
import OptimizationProgressBar from '@/components/optimization/OptimizationProgressBar';

<OptimizationProgressBar
  job={{
    id: "job-uuid",
    job_name: "Optimization Job Name",
    status: "running",
    current_iteration: 150,
    progress_percentage: 45.8,
    started_at: "2025-10-01T10:00:00Z",
    runtime_seconds: 2700,
    estimated_completion_at: "2025-10-01T12:00:00Z"
  }}
  showDetails={true}
/>
```

### Props

- `job`: OptimizationJobProgress object containing:
  - `id`: Unique job identifier
  - `job_name`: Optional job name
  - `status`: Job status (pending, running, completed, failed, cancelled)
  - `current_iteration`: Current iteration number
  - `progress_percentage`: Progress percentage (0-100)
  - `started_at`: ISO timestamp when job started
  - `runtime_seconds`: Total runtime in seconds
  - `estimated_completion_at`: ISO timestamp of estimated completion
- `showDetails`: Boolean to show/hide detailed information (default: true)
- `onUpdate`: Optional callback fired when job updates

### Status Colors

- **Completed**: Green gradient (green-400 to green-600)
- **Running**: Blue gradient with shimmer animation (blue-400 to blue-600)
- **Failed**: Red gradient (red-400 to red-600)
- **Cancelled**: Gray gradient (gray-400 to gray-600)
- **Pending**: Yellow gradient (yellow-400 to yellow-600)

### Auto-Refresh Integration

The `/app/optimize/page.tsx` component implements automatic polling for running jobs:

- Polls every 3 seconds when jobs with `running` or `pending` status exist
- Automatically stops polling when all jobs complete
- Cleans up polling on component unmount or tab switch

### API Endpoints Used

- `GET /api/v1/optimize/jobs` - List all jobs
- `GET /api/v1/optimize/jobs/{job_id}/progress` - Get detailed progress
- `GET /api/v1/optimize/jobs/{job_id}/status` - Get simple status
- `POST /api/v1/optimize/jobs/{job_id}/cancel` - Cancel running job

### Example Implementation

See `frontend/src/app/optimize/page.tsx` lines 426-440 for full implementation example.
