import React, { useState, useEffect, useRef, useCallback } from 'react';
import styled from 'styled-components';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent
} from '@mui/lab';
import {
  Typography,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  Chip,
  CircularProgress
} from '@mui/material';
import {
  DocumentIcon,
  PhotoIcon,
  HeartIcon,
  BeakerIcon,
  ExclamationCircleIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

// Types
interface HealthEvent {
  id: string;
  title: string;
  event_type: 'CHECKUP' | 'MEDICATION' | 'SYMPTOM';
  description: string;
  date_time: string;
  file_paths: string[];
  file_types: string[];
}

interface HealthTimelineProps {
  events: HealthEvent[];
  onLoadMore: () => Promise<void>;
  hasMore: boolean;
}

// Styled Components
const TimelineContainer = styled.div`
  margin-top: 1rem;
  padding: 1rem;
  position: relative;
`;

const TimelineCard = styled.div<{ position: 'left' | 'right' }>`
  cursor: pointer;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s ease;
  text-align: ${props => props.position === 'left' ? 'right' : 'left'};
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  }
`;

const LoadingIndicator = styled.div`
  display: flex;
  justify-content: center;
  padding: 1rem;
`;

// Helper functions
const getEventIcon = (event: HealthEvent) => {
  // First priority: Check file types
  if (event.file_types?.length > 0) {
    const fileType = event.file_types[0];
    if (fileType.includes('pdf')) return <DocumentIcon width={20} />;
    if (fileType.includes('image')) return <PhotoIcon width={20} />;
  }
  
  // Second priority: Event type - ensure lowercase comparison
  switch (event.event_type.toLowerCase()) {
    case 'checkup':
      return <HeartIcon width={20} />;
    case 'medication':
      return <BeakerIcon width={20} />;
    case 'symptom':
      return <ExclamationCircleIcon width={20} />;
    default:
      return <DocumentIcon width={20} />;
  }
};

const getEventColor = (eventType: string) => {
  // Ensure lowercase comparison
  switch (eventType.toLowerCase()) {
    case 'checkup':
      return '#4CAF50';
    case 'medication':
      return '#2196F3';
    case 'symptom':
      return '#F44336';
    default:
      return '#9E9E9E';
  }
};

const HealthTimeline: React.FC<HealthTimelineProps> = ({ events, onLoadMore, hasMore }) => {
  const [selectedEvent, setSelectedEvent] = useState<HealthEvent | null>(null);
  const [loading, setLoading] = useState(false);
  const observer = useRef<IntersectionObserver | null>(null);
  const lastEventRef = useCallback((node: HTMLDivElement) => {
    if (loading) return;
    
    if (observer.current) observer.current.disconnect();
    
    observer.current = new IntersectionObserver(async entries => {
      if (entries[0].isIntersecting && hasMore) {
        setLoading(true);
        await onLoadMore();
        setLoading(false);
      }
    });
    
    if (node) observer.current.observe(node);
  }, [loading, hasMore, onLoadMore]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <TimelineContainer>
      <Timeline position="alternate">
        {events.map((event, index) => (
          <TimelineItem key={event.id}>
            <TimelineOppositeContent>
              <Typography variant="subtitle2" color="textSecondary">
                {formatDate(event.date_time)}
              </Typography>
            </TimelineOppositeContent>
            
            <TimelineSeparator>
              <TimelineDot sx={{ bgcolor: getEventColor(event.event_type) }}>
                {getEventIcon(event)}
              </TimelineDot>
              {index < events.length - 1 && <TimelineConnector />}
            </TimelineSeparator>
            
            <TimelineContent>
              <TimelineCard
                ref={index === events.length - 1 ? lastEventRef : null}
                onClick={() => setSelectedEvent(event)}
                position={index % 2 === 0 ? 'right' : 'left'}
              >
                <Typography variant="h6" sx={{ mt: 1 }}>
                  {event.title}
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                  {event.description.substring(0, 100)}
                  {event.description.length > 100 ? '...' : ''}
                </Typography>
                
                {event.file_paths?.length > 0 && (
                  <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap', justifyContent: index % 2 === 0 ? 'flex-start' : 'flex-end' }}>
                    {event.file_paths.map((path, i) => (
                      <Chip
                        key={i}
                        size="small"
                        icon={event.file_types[i]?.includes('pdf') ? <DocumentIcon width={16} /> : <PhotoIcon width={16} />}
                        label={path.split('/').pop()}
                      />
                    ))}
                  </Box>
                )}
              </TimelineCard>
            </TimelineContent>
          </TimelineItem>
        ))}
      </Timeline>
      
      {loading && (
        <LoadingIndicator>
          <CircularProgress size={24} />
        </LoadingIndicator>
      )}

      {/* Event Detail Modal */}
      <Dialog
        open={!!selectedEvent}
        onClose={() => setSelectedEvent(null)}
        maxWidth="md"
        fullWidth
      >
        {selectedEvent && (
          <>
            <DialogTitle>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Typography variant="h6">{selectedEvent.title}</Typography>
                <IconButton onClick={() => setSelectedEvent(null)} size="small">
                  <XMarkIcon width={20} />
                </IconButton>
              </Box>
            </DialogTitle>
            <DialogContent>
              <Typography variant="subtitle1" color="textSecondary">
                {formatDate(selectedEvent.date_time)}
              </Typography>
              <Typography variant="body1" sx={{ mt: 2 }}>
                {selectedEvent.description}
              </Typography>
              
              {selectedEvent.file_paths?.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="h6">Attachments</Typography>
                  <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {selectedEvent.file_paths.map((path, i) => (
                      <Chip
                        key={i}
                        size="small"
                        icon={selectedEvent.file_types[i]?.includes('pdf') ? <DocumentIcon width={16} /> : <PhotoIcon width={16} />}
                        label={path.split('/').pop()}
                        onClick={() => window.open(path, '_blank')}
                      />
                    ))}
                  </Box>
                </Box>
              )}
            </DialogContent>
          </>
        )}
      </Dialog>
    </TimelineContainer>
  );
};

export default HealthTimeline; 