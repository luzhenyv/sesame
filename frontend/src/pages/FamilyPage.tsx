import React, { useState, useEffect } from 'react';
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
import HealthTimeline from '../components/HealthTimeline.tsx';

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
  title: string;
  event_type: 'CHECKUP' | 'MEDICATION' | 'SYMPTOM';
  description: string;
  date_time: string;
  file_paths: string[];
  file_types: string[];
  family_member: string;
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
    title: 'Annual Physical',
    event_type: 'CHECKUP',
    description: 'Regular checkup with Dr. Smith',
    date_time: '2024-03-15',
    file_paths: ['report.pdf'],
    file_types: ['pdf'],
    family_member: 'John'
  },
  // Add more mock events as needed
];

const FamilyPage: React.FC = () => {
  const [timeRange, setTimeRange] = useState('month');
  const [selectedFilters, setSelectedFilters] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isCreateEventModalOpen, setIsCreateEventModalOpen] = useState(false);
  const [healthEvents, setHealthEvents] = useState<HealthEvent[]>([]);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);
  
  const fetchHealthEvents = async (pageNum: number) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/v1/health-events?page=${pageNum}&per_page=5`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      });
      
      if (!response.ok) throw new Error('Failed to fetch health events');
      
      const data = await response.json();
      if (pageNum === 1) {
        setHealthEvents(data.items);
      } else {
        setHealthEvents(prev => [...prev, ...data.items]);
      }
      setHasMore(data.items.length === 5);
    } catch (error) {
      console.error('Error fetching health events:', error);
    }
  };

  useEffect(() => {
    fetchHealthEvents(1);
  }, []);

  const handleLoadMore = async () => {
    const nextPage = page + 1;
    await fetchHealthEvents(nextPage);
    setPage(nextPage);
  };

  const handleEventSubmit = async (eventData: any) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/health-events', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(eventData),
      });

      if (!response.ok) throw new Error('Failed to create event');

      // Refresh the events list
      setPage(1);
      await fetchHealthEvents(1);
    } catch (error) {
      console.error('Error creating event:', error);
    }
  };

  return (
    <Container>
      <MainContent>
        <FamilyDashboard />

        {/* Health Timeline Section */}
        <Section>
          <SectionTitle>
            Health Timeline
            <CreateEventButton onClick={() => setIsCreateEventModalOpen(true)}>
              <span>+</span> Create Event
            </CreateEventButton>
          </SectionTitle>
          
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
                      <Typography key={value} component="span" sx={{ mr: 0.5 }}>
                        {value}
                      </Typography>
                    ))}
                  </Box>
                )}
              >
                {/* Add family member options here */}
              </Select>
            </FormControl>
          </FilterBar>

          <HealthTimeline
            events={healthEvents}
            onLoadMore={handleLoadMore}
            hasMore={hasMore}
          />
        </Section>

        <CreateEventModal
          open={isCreateEventModalOpen}
          onClose={() => setIsCreateEventModalOpen(false)}
          onSubmit={handleEventSubmit}
          familyMembers={[]} // Add your family members data here
        />
      </MainContent>
    </Container>
  );
};

export default FamilyPage; 