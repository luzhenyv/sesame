import React, { useState } from 'react';
import styled from 'styled-components';
import { 
  TextField, 
  Button, 
  Chip,
  Pagination,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { MagnifyingGlassIcon, CalendarIcon, ClockIcon } from '@heroicons/react/24/outline';

interface BlogPost {
  id: number;
  title: string;
  author: string;
  date: string;
  tags: string[];
  readTime: string;
  excerpt: string;
  image: string;
  category: string;
  likes: number;
  comments: number;
}

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
`;

const PageHeader = styled.div`
  margin-bottom: 2rem;
  
  h1 {
    font-size: 2.5rem;
    color: #2c3e50;
    margin-bottom: 1rem;
  }
  
  p {
    color: #666;
    font-size: 1.1rem;
    max-width: 800px;
  }
`;

const FilterSection = styled.div`
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  align-items: end;
`;

const BlogGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
`;

const BlogCard = styled.article`
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
`;

const BlogImage = styled.img`
  width: 100%;
  height: 200px;
  object-fit: cover;
`;

const BlogContent = styled.div`
  padding: 1.5rem;
`;

const BlogTitle = styled.h2`
  margin: 0 0 1rem 0;
  font-size: 1.25rem;
  color: #2c3e50;
  line-height: 1.4;
`;

const BlogMeta = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  color: #666;
`;

const TagsContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 1rem 0;
`;

const PaginationContainer = styled.div`
  display: flex;
  justify-content: center;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #eee;
`;

const BlogPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [sortBy, setSortBy] = useState('recent');
  const [currentPage, setCurrentPage] = useState(1);

  // Mock data - replace with API call
  const blogPosts: BlogPost[] = [
    {
      id: 1,
      title: '10 Evidence-Based Ways to Improve Your Mental Health',
      author: 'Dr. Sarah Johnson',
      date: '2024-03-15',
      tags: ['Mental Health', 'Wellness', 'Self-Care'],
      readTime: '8 min read',
      excerpt: 'Discover scientifically-proven methods to enhance your mental well-being and build resilience in your daily life.',
      image: '/assets/images/mental-health.jpg',
      category: 'Mental Health',
      likes: 245,
      comments: 18
    },
    {
      id: 2,
      title: 'The Science Behind Quality Sleep',
      author: 'Dr. Michael Chen',
      date: '2024-03-14',
      tags: ['Sleep', 'Physical Health', 'Lifestyle'],
      readTime: '6 min read',
      excerpt: 'Understanding sleep cycles and how to optimize your rest for better health and productivity.',
      image: '/assets/images/sleep.jpg',
      category: 'Physical Health',
      likes: 189,
      comments: 12
    },
    {
      id: 3,
      title: 'Nutrition Myths Debunked',
      author: 'Emma Wilson, RD',
      date: '2024-03-13',
      tags: ['Nutrition', 'Diet', 'Health Facts'],
      readTime: '10 min read',
      excerpt: 'Separating fact from fiction in the world of nutrition and dietary advice.',
      image: '/assets/images/nutrition.jpg',
      category: 'Nutrition',
      likes: 156,
      comments: 23
    },
    {
      id: 4,
      title: 'Building Healthy Exercise Habits',
      author: 'James Thompson',
      date: '2024-03-12',
      tags: ['Exercise', 'Fitness', 'Lifestyle'],
      readTime: '7 min read',
      excerpt: 'Learn how to create and maintain sustainable exercise habits that fit your lifestyle.',
      image: '/assets/images/exercise.jpg',
      category: 'Fitness',
      likes: 178,
      comments: 15
    }
  ];

  return (
    <Container>
      <MainContent>
        <PageHeader>
          <h1>Health & Wellness Blog</h1>
          <p>
            Expert insights, latest research, and practical advice to help you live 
            a healthier, more balanced life.
          </p>
        </PageHeader>

        <FilterSection>
          <TextField
            fullWidth
            placeholder="Search articles..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: <MagnifyingGlassIcon width={20} />,
            }}
          />

          <FormControl fullWidth>
            <InputLabel>Category</InputLabel>
            <Select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              label="Category"
            >
              <MenuItem value="all">All Categories</MenuItem>
              <MenuItem value="mental">Mental Health</MenuItem>
              <MenuItem value="physical">Physical Health</MenuItem>
              <MenuItem value="nutrition">Nutrition</MenuItem>
              <MenuItem value="lifestyle">Lifestyle</MenuItem>
            </Select>
          </FormControl>

          <FormControl fullWidth>
            <InputLabel>Sort By</InputLabel>
            <Select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              label="Sort By"
            >
              <MenuItem value="recent">Most Recent</MenuItem>
              <MenuItem value="popular">Most Popular</MenuItem>
              <MenuItem value="trending">Trending</MenuItem>
            </Select>
          </FormControl>
        </FilterSection>

        <BlogGrid>
          {blogPosts.map(post => (
            <BlogCard key={post.id}>
              <BlogImage src={post.image} alt={post.title} />
              <BlogContent>
                <BlogMeta>
                  <span>{post.category}</span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <ClockIcon width={16} />
                    {post.readTime}
                  </span>
                </BlogMeta>

                <BlogTitle>{post.title}</BlogTitle>

                <TagsContainer>
                  {post.tags.map(tag => (
                    <Chip 
                      key={tag} 
                      label={tag} 
                      size="small" 
                      variant="outlined" 
                    />
                  ))}
                </TagsContainer>

                <p style={{ color: '#666', margin: '1rem 0' }}>{post.excerpt}</p>

                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginTop: '1rem' 
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <CalendarIcon width={16} />
                    <span style={{ color: '#666' }}>
                      {new Date(post.date).toLocaleDateString()}
                    </span>
                  </div>
                  <span style={{ color: '#666' }}>By {post.author}</span>
                </div>

                <Button 
                  variant="contained" 
                  fullWidth 
                  style={{ marginTop: '1rem' }}
                >
                  Read Article
                </Button>

                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between',
                  marginTop: '1rem',
                  color: '#666',
                  fontSize: '0.9rem'
                }}>
                  <span>❤️ {post.likes} likes</span>
                  <span>💬 {post.comments} comments</span>
                </div>
              </BlogContent>
            </BlogCard>
          ))}
        </BlogGrid>

        <PaginationContainer>
          <Pagination 
            count={10} 
            page={currentPage}
            onChange={(_, page) => setCurrentPage(page)}
            color="primary"
          />
        </PaginationContainer>
      </MainContent>
    </Container>
  );
};

export default BlogPage; 