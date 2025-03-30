import React, { useState } from 'react';
import styled from 'styled-components';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line
} from 'recharts';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot
} from '@mui/lab';
import {
  Card,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  IconButton,
  TextField,
  Chip,
  Typography,
  Box,
  Alert,
  Tooltip as MuiTooltip
} from '@mui/material';
import {
  CalendarIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  DocumentIcon,
  ExclamationCircleIcon
} from '@heroicons/react/24/outline';
import FamilyDashboard from '../components/FamilyDashboard.tsx';
import CreateEventModal from '../components/CreateEventModal.tsx';

// Types
interface HealthScore {
  category: string;
  score: number;
  status: 'good' | 'warning' | 'attention';
}

interface FamilyMember {
  id: string;
  name: string;
  role: string;
  avatar: string;
  healthScore: number;
  riskLevel: 'low' | 'medium' | 'high';
}

interface HealthEvent {
  id: string;
  date: string;
  type: 'checkup' | 'medication' | 'symptom' | 'other';
  title: string;
  description: string;
  familyMember: string;
  attachments?: string[];
}

// Styled Components
const Container = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f8f9fa;
  color: #333;
  font-family: 'Roboto', sans-serif;
  width: 100%;
  box-sizing: border-box;
`;

const MainContent = styled.main`
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  box-sizing: border-box;
  
  @media (max-width: 768px) {
    padding: 1rem;
  }
`;

const Section = styled(Card)`
  padding: 1.5rem;
  border-radius: 12px;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
`;

const SectionTitle = styled.h2`
  color: #1a1a1a;
  font-size: 1.5rem;
  margin: 0 0 1.5rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const ScoreCard = styled(Card)`
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: ${props => props.color || 'white'};
  transition: transform 0.2s;
  
  &:hover {
    transform: translateY(-4px);
  }
`;

const TimelineContainer = styled.div`
  margin-top: 2rem;
  padding: 1rem;
`;

const CreateEventButton = styled.button`
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 20px;
  padding: 0.6rem 1.2rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.3s ease;
  margin-left: auto;
  
  &:hover {
    background-color: #2980b9;
  }
`;

const FilterBar = styled.div`
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  
  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

// Mock Data
const mockFamilyMembers: FamilyMember[] = [
  { id: '1', name: 'John (You)', role: 'self', avatar: '👨', healthScore: 80, riskLevel: 'low' },
  { id: '2', name: 'Sarah', role: 'spouse', avatar: '👩', healthScore: 85, riskLevel: 'low' },
  { id: '3', name: 'Tommy', role: 'child', avatar: '👦', healthScore: 90, riskLevel: 'low' },
  { id: '4', name: 'Max', role: 'pet', avatar: '🐕', healthScore: 75, riskLevel: 'medium' },
];

const mockHealthEvents: HealthEvent[] = [
  {
    id: '1',
    date: '2024-03-15',
    type: 'checkup',
    title: 'Annual Physical',
    description: 'Regular checkup with Dr. Smith',
    familyMember: 'John',
    attachments: ['report.pdf']
  },
  // Add more mock events as needed
];

const FamilyPage: React.FC = () => {
  const [timeRange, setTimeRange] = useState('month');
  const [selectedFilters, setSelectedFilters] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isCreateEventModalOpen, setIsCreateEventModalOpen] = useState(false);
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'good': return '#4CAF50';
      case 'warning': return '#FFC107';
      case 'attention': return '#F44336';
      default: return '#666666';
    }
  };

  // Mock data for the dashboard
  const familyMembers = [
    { id: '1', name: 'Dad', role: 'father', avatar: '😊', healthScore: 92 },
    { id: '2', name: 'Mom', role: 'mother', avatar: '👩', healthScore: 88 },
    { id: '3', name: 'Son', role: 'son', avatar: '👦', healthScore: 75 },
    { id: '4', name: 'Daughter', role: 'daughter', avatar: '👧', healthScore: 65 },
  ];

  const handleAddMember = () => {
    // Implement add member functionality
    console.log('Add member clicked');
  };

  const handleCreateEvent = () => {
    setIsCreateEventModalOpen(true);
  };

  const handleEventSubmit = (eventData: any) => {
    // TODO: Implement event submission to backend
    console.log('Event data:', eventData);
  };

  return (
    <Container>
      <MainContent>
        {/* Replace the old sections with the new dashboard */}
        <FamilyDashboard
          familyScore={85}
          memberCount={familyMembers.length}
          members={familyMembers}
          onAddMember={handleAddMember}
        />

        {/* Health Timeline Section */}
        <Section>
          <SectionTitle>
            Health Timeline
            <CreateEventButton onClick={handleCreateEvent}>
              <span>+</span> Create Event
            </CreateEventButton>
          </SectionTitle>
          
          <FilterBar>
            <TextField
              placeholder="Search events..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              inputProps={{
                startAdornment: <MagnifyingGlassIcon width={20} />,
              }}
            />
            
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Filter by Member</InputLabel>
              <Select
                multiple
                value={selectedFilters}
                onChange={(e) => setSelectedFilters(typeof e.target.value === 'string' ? e.target.value.split(',') : e.target.value)}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value) => (
                      <Chip key={value} label={value} />
                    ))}
                  </Box>
                )}
              >
                {mockFamilyMembers.map(member => (
                  <MenuItem key={member.id} value={member.name}>
                    {member.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </FilterBar>

          <TimelineContainer>
            <Timeline>
              {mockHealthEvents.map((event) => (
                <TimelineItem key={event.id}>
                  <TimelineSeparator>
                    <TimelineDot color={
                      event.type === 'checkup' ? 'primary' :
                      event.type === 'medication' ? 'secondary' :
                      event.type === 'symptom' ? 'error' : 'grey'
                    } />
                    <TimelineConnector />
                  </TimelineSeparator>
                  <TimelineContent>
                    <Typography variant="h6" component="span">
                      {event.title}
                    </Typography>
                    <Typography color="textSecondary">
                      {new Date(event.date).toLocaleDateString()}
                    </Typography>
                    <Typography>{event.description}</Typography>
                    {event.attachments && (
                      <Box sx={{ mt: 1 }}>
                        {event.attachments.map(attachment => (
                          <Chip
                            key={attachment}
                            icon={<DocumentIcon width={16} />}
                            label={attachment}
                            size="small"
                            sx={{ mr: 1 }}
                          />
                        ))}
                      </Box>
                    )}
                  </TimelineContent>
                </TimelineItem>
              ))}
            </Timeline>
          </TimelineContainer>
        </Section>

        <CreateEventModal
          open={isCreateEventModalOpen}
          onClose={() => setIsCreateEventModalOpen(false)}
          onSubmit={handleEventSubmit}
          familyMembers={mockFamilyMembers}
        />
      </MainContent>
    </Container>
  );
};

export default FamilyPage; 