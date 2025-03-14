import React, { useState } from 'react';
import styled from 'styled-components';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
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
`;

const MainContent = styled.main`
  flex: 1;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 2rem;
`;

const Section = styled(Card)`
  padding: 1.5rem;
  border-radius: 12px;
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
const mockPersonalScores: HealthScore[] = [
  { category: 'Physical Health', score: 85, status: 'good' },
  { category: 'Mental Health', score: 75, status: 'warning' },
  { category: 'Lifestyle Habits', score: 90, status: 'good' },
  { category: 'Medical Indicators', score: 70, status: 'attention' },
];

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
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'good': return '#4CAF50';
      case 'warning': return '#FFC107';
      case 'attention': return '#F44336';
      default: return '#666666';
    }
  };

  return (
    <Container>
      <MainContent>
        {/* Personal Health Score Section */}
        <Section>
          <SectionTitle>
            Personal Health Score
            <MuiTooltip title="Your overall health assessment based on various factors">
              <ExclamationCircleIcon width={20} />
            </MuiTooltip>
          </SectionTitle>
          
          <Alert severity="info" sx={{ mb: 2 }}>
            Upload additional health data to improve score accuracy
          </Alert>
          
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={mockPersonalScores}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="category" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar
                dataKey="score"
                fill="#8884d8"
                label={{ position: 'top' }}
                background={{ fill: '#eee' }}
              />
            </BarChart>
          </ResponsiveContainer>
        </Section>

        {/* Family Health Scores Section */}
        <Section>
          <SectionTitle>Family Health Scores</SectionTitle>
          
          <FormControl sx={{ mb: 2, minWidth: 200 }}>
            <InputLabel>Time Period</InputLabel>
            <Select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              label="Time Period"
            >
              <MenuItem value="week">Week</MenuItem>
              <MenuItem value="month">Month</MenuItem>
              <MenuItem value="year">Year</MenuItem>
            </Select>
          </FormControl>

          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 3 }}>
            {mockFamilyMembers.map(member => (
              <ScoreCard
                key={member.id}
                color={member.riskLevel === 'low' ? '#e8f5e9' : 
                       member.riskLevel === 'medium' ? '#fff3e0' : '#ffebee'}
              >
                <Typography variant="h1" sx={{ fontSize: '3rem', textAlign: 'center' }}>
                  {member.avatar}
                </Typography>
                <Typography variant="h6" align="center">{member.name}</Typography>
                <Typography variant="body2" align="center">
                  Health Score: {member.healthScore}
                </Typography>
              </ScoreCard>
            ))}
          </Box>

          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={mockFamilyMembers}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="healthScore" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        </Section>

        {/* Health Timeline Section */}
        <Section>
          <SectionTitle>Health Timeline</SectionTitle>
          
          <FilterBar>
            <TextField
              placeholder="Search events..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
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
      </MainContent>
    </Container>
  );
};

export default FamilyPage; 