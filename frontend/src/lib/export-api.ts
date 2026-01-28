// API service for export functionality
import api from './api';

export interface ExportTemplate {
  id: number;
  name: string;
  description: string;
  format: 'svg' | 'pdf' | 'png' | 'figma';
  format_display: string;
  quality: 'low' | 'medium' | 'high' | 'ultra';
  quality_display: string;
  optimize: boolean;
  include_metadata: boolean;
  compression: string;
  width: number | null;
  height: number | null;
  scale: number;
  format_options: Record<string, unknown>;
  use_count: number;
  created_at: string;
}

export interface ExportJob {
  id: number;
  user: number;
  user_name: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  status_display: string;
  format: string;
  template_name: string | null;
  total_projects: number;
  completed_projects: number;
  failed_projects: number;
  progress_percentage: number;
  file_size: number;
  duration: number | null;
  error_message: string;
  created_at: string;
  file_url?: string;
  project_count?: number;
  progress?: number;
}

class ExportAPI {
  // Single exports
  async exportToSVG(projectId: number) {
    const response = await api.post(`/projects/projects/${projectId}/export_svg/`, {}, {
      responseType: 'blob'
    });
    return response.data;
  }

  async exportToPDF(projectId: number) {
    const response = await api.post(`/projects/projects/${projectId}/export_pdf/`, {}, {
      responseType: 'blob'
    });
    return response.data;
  }

  async exportToFigma(projectId: number) {
    const response = await api.get(`/projects/projects/${projectId}/export_figma/`, {
      responseType: 'blob'
    });
    return response.data;
  }

  // Export Templates
  async getTemplates() {
    const response = await api.get('/projects/export-templates/');
    return response.data;
  }

  async createTemplate(data: Partial<ExportTemplate>) {
    const response = await api.post('/projects/export-templates/', data);
    return response.data;
  }

  async updateTemplate(id: number, data: Partial<ExportTemplate>) {
    const response = await api.patch(`/projects/export-templates/${id}/`, data);
    return response.data;
  }

  async deleteTemplate(id: number) {
    await api.delete(`/projects/export-templates/${id}/`);
  }

  async useTemplate(templateId: number, projectId: number) {
    const response = await api.post(`/projects/export-templates/${templateId}/use_template/`, {
      project_id: projectId
    }, {
      responseType: 'blob'
    });
    return response.data;
  }

  // Batch Export
  async createBatchExport(projectIds: number[], format: string, templateId?: number) {
    const data: {
      project_ids: number[];
      format: string;
      template_id?: number;
    } = {
      project_ids: projectIds,
      format: format
    };
    
    if (templateId) {
      data.template_id = templateId;
    }
    
    const response = await api.post('/projects/export-jobs/batch_export/', data);
    return response.data;
  }

  async getExportJobs() {
    const response = await api.get('/projects/export-jobs/');
    return response.data;
  }

  async getExportJobStatus(jobId: number) {
    const response = await api.get(`/projects/export-jobs/${jobId}/status/`);
    return response.data;
  }

  async downloadExportJob(jobId: number) {
    const response = await api.get(`/projects/export-jobs/${jobId}/download/`, {
      responseType: 'blob'
    });
    return response.data;
  }

  // Helper to trigger download
  downloadBlob(blob: Blob, filename: string) {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  }
}

export const exportAPI = new ExportAPI();
