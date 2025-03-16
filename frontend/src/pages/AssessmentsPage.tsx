import React, { useState } from 'react';
import styled from 'styled-components';
import { 
  Container, 
  Typography, 
  Box,
  Card, 
  CardContent, 
  Button, 
  TextField,
  InputAdornment,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { MagnifyingGlassIcon, FunnelIcon } from '@heroicons/react/24/outline';

// Import the HealthAssessment interface from HomePage if needed
import { HealthAssessment } from './HomePage';

// Styled Components
const PageContainer = styled(Container)`
  padding-top: 2rem;
  padding-bottom: 4rem;
  min-height: 80vh;
  background-color: #f8f9fa;
`;

const PageTitle = styled(Typography)`
  margin-bottom: 2rem;
  font-weight: 600;
`;

const FilterSection = styled(Box)`
  margin-bottom: 2rem;
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
`;

const AssessmentCard = styled(Card)`
  height: 100%;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  }
`;

const CategoryChip = styled(Chip)`
  margin-bottom: 1rem;
`;

const AssessmentIcon = styled.span`
  font-size: 2.5rem;
  display: block;
  margin-bottom: 1rem;
`;

const DifficultyIndicator = styled.div<{ difficulty: string }>`
  color: ${props => 
    props.difficulty === 'Easy' ? '#4CAF50' :
    props.difficulty === 'Medium' ? '#FFC107' : '#F44336'
  };
  font-weight: 500;
  margin-top: 0.5rem;
`;

const AssessmentsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [difficultyFilter, setDifficultyFilter] = useState('');

  // Mock data - expanded from HomePage
  const assessments: HealthAssessment[] = [
    {
      id: 1,
      name: 'Mental Wellness Check',
      category: 'Mental Health',
      description: 'Evaluate your emotional well-being and stress levels with our comprehensive assessment. This test helps identify potential areas of concern and provides personalized recommendations.',
      time: '10-15 mins',
      difficulty: 'Medium',
      icon: '🧠'
    },
    {
      id: 2,
      name: 'Sleep Quality Analysis',
      category: 'Physical Health',
      description: 'Assess your sleep patterns and get improvement tips based on your responses. Our sleep analysis looks at duration, quality, and habits to help you get better rest.',
      time: '5-8 mins',
      difficulty: 'Easy',
      icon: '🌙'
    },
    {
      id: 3,
      name: 'Cognitive Function Test',
      category: 'Mental Health',
      description: 'Measure memory, focus, and problem-solving skills with our interactive cognitive assessment. This test evaluates multiple dimensions of cognitive performance.',
      time: '15-20 mins',
      difficulty: 'Advanced',
      icon: '🧩'
    },
    {
      id: 4,
      name: 'Fitness Level Check',
      category: 'Physical Health',
      description: 'Evaluate your cardiovascular endurance and strength through a series of questions and self-reported metrics. Get a baseline of your current fitness level.',
      time: '10-12 mins',
      difficulty: 'Medium',
      icon: '🏋️‍♂️'
    },
    {
      id: 5,
      name: 'Social Wellness Quiz',
      category: 'Social Health',
      description: 'Assess your relationship quality and social habits to understand your social wellness. This assessment helps identify areas for improving your social connections.',
      time: '8-10 mins',
      difficulty: 'Easy',
      icon: '👥'
    },
    {
      id: 6,
      name: 'Nutrition Assessment',
      category: 'Physical Health',
      description: 'Analyze your eating habits and nutritional intake to identify potential improvements. Get personalized recommendations for a balanced diet.',
      time: '12-15 mins',
      difficulty: 'Medium',
      icon: '🥗'
    },
    {
      id: 7,
      name: 'Anxiety Screening',
      category: 'Mental Health',
      description: 'Screen for symptoms of anxiety with this clinically-validated assessment tool. Understand your anxiety levels and get resources for management.',
      time: '7-10 mins',
      difficulty: 'Easy',
      icon: '😰'
    },
    {
      id: 8,
      name: 'Work-Life Balance Evaluation',
      category: 'Lifestyle',
      description: 'Evaluate how well you balance your professional and personal life. Identify potential stressors and areas for improvement.',
      time: '10-12 mins',
      difficulty: 'Medium',
      icon: '⚖️'
    },
    {
      id: 9,
      name: 'Comprehensive Health Risk Assessment',
      category: 'General Health',
      description: 'A thorough evaluation of various health factors to identify potential risks and preventative measures. Covers multiple health domains.',
      time: '20-25 mins',
      difficulty: 'Advanced',
      icon: '📊'
    },
    {
      id: 10,
      name: 'Digital Wellbeing Check',
      category: 'Lifestyle',
      description: 'Assess your relationship with technology and screen time. Learn strategies for healthier digital habits.',
      time: '8-10 mins',
      difficulty: 'Easy',
      icon: '📱'
    },
    {
      id: 11,
      name: 'Stress Resilience Test',
      category: 'Mental Health',
      description: 'Measure your ability to cope with and recover from stress. Identify your resilience strengths and areas for development.',
      time: '12-15 mins',
      difficulty: 'Medium',
      icon: '🛡️'
    },
    {
      id: 12,
      name: 'Cardiovascular Health Check',
      category: 'Physical Health',
      description: 'Evaluate risk factors related to heart health based on lifestyle, family history, and other factors. Get personalized heart health recommendations.',
      time: '15-18 mins',
      difficulty: 'Advanced',
      icon: '❤️'
    }
  ];

  // Filter assessments based on search term and filters
  const filteredAssessments = assessments.filter(assessment => {
    const matchesSearch = assessment.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                         assessment.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = categoryFilter ? assessment.category === categoryFilter : true;
    const matchesDifficulty = difficultyFilter ? assessment.difficulty === difficultyFilter : true;
    
    return matchesSearch && matchesCategory && matchesDifficulty;
  });

  // Get unique categories for filter
  const categories = Array.from(new Set(assessments.map(a => a.category)));
  const difficulties = ['Easy', 'Medium', 'Advanced'];

  return (
    <PageContainer maxWidth="lg">
      <PageTitle variant="h4">
        Health Assessments
      </PageTitle>
      
      <FilterSection>
        <TextField
          placeholder="Search assessments..."
          variant="outlined"
          size="small"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ flexGrow: 1, minWidth: '250px' }}
          slotProps={{
            input: {
              startAdornment: (
                <InputAdornment position="start">
                  <MagnifyingGlassIcon width={20} />
                </InputAdornment>
              ),
            }
          }}
        />
        
        <FormControl size="small" sx={{ minWidth: '150px' }}>
          <InputLabel>Category</InputLabel>
          <Select
            value={categoryFilter}
            label="Category"
            onChange={(e) => setCategoryFilter(e.target.value)}
          >
            <MenuItem value="">All Categories</MenuItem>
            {categories.map(category => (
              <MenuItem key={category} value={category}>{category}</MenuItem>
            ))}
          </Select>
        </FormControl>
        
        <FormControl size="small" sx={{ minWidth: '150px' }}>
          <InputLabel>Difficulty</InputLabel>
          <Select
            value={difficultyFilter}
            label="Difficulty"
            onChange={(e) => setDifficultyFilter(e.target.value)}
          >
            <MenuItem value="">All Difficulties</MenuItem>
            {difficulties.map(difficulty => (
              <MenuItem key={difficulty} value={difficulty}>{difficulty}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </FilterSection>
      
      <Typography variant="body1" color="textSecondary" paragraph>
        Showing {filteredAssessments.length} of {assessments.length} assessments
      </Typography>
      
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: {
          xs: '1fr',
          sm: 'repeat(2, 1fr)',
          md: 'repeat(3, 1fr)'
        },
        gap: 3
      }}>
        {filteredAssessments.map(assessment => (
          <AssessmentCard key={assessment.id}>
            <CardContent>
              <AssessmentIcon>{assessment.icon}</AssessmentIcon>
              <CategoryChip 
                label={assessment.category} 
                size="small" 
                color="primary" 
                variant="outlined"
              />
              <Typography variant="h6" component="h2" gutterBottom>
                {assessment.name}
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                {assessment.description}
              </Typography>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Typography variant="body2">
                  ⏱ {assessment.time}
                </Typography>
                <DifficultyIndicator difficulty={assessment.difficulty}>
                  {assessment.difficulty}
                </DifficultyIndicator>
              </Box>
              <Button 
                variant="contained" 
                color="primary" 
                fullWidth 
                sx={{ mt: 2 }}
              >
                Start Assessment
              </Button>
            </CardContent>
          </AssessmentCard>
        ))}
      </Box>
      
      {filteredAssessments.length === 0 && (
        <Box textAlign="center" py={5}>
          <Typography variant="h6" color="textSecondary">
            No assessments found matching your criteria
          </Typography>
          <Button 
            variant="outlined" 
            color="primary" 
            sx={{ mt: 2 }}
            onClick={() => {
              setSearchTerm('');
              setCategoryFilter('');
              setDifficultyFilter('');
            }}
          >
            Clear Filters
          </Button>
        </Box>
      )}
    </PageContainer>
  );
};

export default AssessmentsPage; 