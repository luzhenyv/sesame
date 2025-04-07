import React, { useState } from 'react';
import styled from 'styled-components';
import { 
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  IconButton,
  Typography,
  SelectChangeEvent
} from '@mui/material';
import { XMarkIcon, DocumentIcon, MicrophoneIcon } from '@heroicons/react/24/outline';

interface CreateEventModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (eventData: any) => void;
  familyMembers: Array<{ id: string; name: string }>;
}

const ModalContent = styled(DialogContent)`
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
`;

const FileUploadArea = styled.div`
  border: 2px dashed #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #3498db;
    background-color: #f8f9fa;
  }
`;

const FileList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
`;

const FileChip = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #f1f1f1;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
`;

const VoiceInputButton = styled(IconButton)`
  background-color: #f1f1f1;
  margin-left: 0.5rem;
  
  &:hover {
    background-color: #e0e0e0;
  }
`;

const CreateEventModal: React.FC<CreateEventModalProps> = ({
  open,
  onClose,
  onSubmit,
  familyMembers
}) => {
  const [formData, setFormData] = useState({
    title: '',
    event_type: '',
    description: '',
    family_member_id: '',
    date_time: '',
    files: [] as File[]
  });

  const handleTextChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSelectChange = (e: SelectChangeEvent) => {
    const { name, value } = e.target;
    const fieldMap: { [key: string]: string } = {
      type: 'event_type',
      familyMember: 'family_member_id'
    };
    const fieldName = fieldMap[name] || name;
    setFormData(prev => ({ ...prev, [fieldName]: value }));
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      setFormData(prev => ({
        ...prev,
        files: [...prev.files, ...Array.from(files)]
      }));
    }
  };

  const handleRemoveFile = (index: number) => {
    setFormData(prev => ({
      ...prev,
      files: prev.files.filter((_, i) => i !== index)
    }));
  };

  const handleVoiceInput = () => {
    // TODO: Implement voice input functionality
    console.log('Voice input clicked');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const eventData = {
      ...formData,
      date_time: new Date(formData.date_time).toISOString(),
    };
    onSubmit(eventData);
    onClose();
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">Create New Health Event</Typography>
          <IconButton onClick={onClose} size="small">
            <XMarkIcon width={20} />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <form onSubmit={handleSubmit}>
        <ModalContent>
          <TextField
            required
            fullWidth
            label="Event Title"
            name="title"
            value={formData.title}
            onChange={handleTextChange}
          />

          <FormControl fullWidth required>
            <InputLabel>Event Type</InputLabel>
            <Select
              name="type"
              value={formData.event_type}
              onChange={handleSelectChange}
              label="Event Type"
            >
              <MenuItem value="CHECKUP">CHECKUP</MenuItem>
              <MenuItem value="MEDICATION">MEDICATION</MenuItem>
              <MenuItem value="SYMPTOM">SYMPTOM</MenuItem>
            </Select>
          </FormControl>

          <FormControl fullWidth required>
            <InputLabel>Family Member</InputLabel>
            <Select
              name="familyMember"
              value={formData.family_member_id}
              onChange={handleSelectChange}
              label="Family Member"
            >
              {familyMembers.map(member => (
                <MenuItem key={member.id} value={member.id}>
                  {member.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            required
            fullWidth
            type="datetime-local"
            label="Date & Time"
            name="date_time"
            value={formData.date_time}
            onChange={handleTextChange}
            InputLabelProps={{ shrink: true }}
          />

          <Box display="flex" alignItems="flex-start" gap={1}>
            <TextField
              required
              fullWidth
              multiline
              rows={4}
              label="Description"
              name="description"
              value={formData.description}
              onChange={handleTextChange}
            />
            <VoiceInputButton
              onClick={handleVoiceInput}
              size="small"
              title="Use voice input"
            >
              <MicrophoneIcon width={20} />
            </VoiceInputButton>
          </Box>

          <FileUploadArea>
            <input
              type="file"
              multiple
              accept="image/*,.pdf"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
              id="file-upload"
            />
            <label htmlFor="file-upload">
              <Box display="flex" flexDirection="column" alignItems="center" gap={1}>
                <DocumentIcon width={32} />
                <Typography>
                  Drag and drop files here or click to upload
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Supported formats: Images and PDFs
                </Typography>
              </Box>
            </label>

            {formData.files.length > 0 && (
              <FileList>
                {formData.files.map((file, index) => (
                  <FileChip key={index}>
                    <DocumentIcon width={16} />
                    <Typography>{file.name}</Typography>
                    <IconButton
                      size="small"
                      onClick={() => handleRemoveFile(index)}
                    >
                      <XMarkIcon width={16} />
                    </IconButton>
                  </FileChip>
                ))}
              </FileList>
            )}
          </FileUploadArea>
        </ModalContent>

        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={!formData.title || !formData.event_type || !formData.family_member_id || !formData.date_time || !formData.description}
          >
            Create Event
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default CreateEventModal; 