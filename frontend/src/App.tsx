import React from 'react';
import { ThemeProvider, createTheme, CssBaseline, Container, Box } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import TranscriptUpload from './components/TranscriptUpload';
import TranscriptQuery from './components/TranscriptQuery';
import TranscriptList from './components/TranscriptList';

// Create a theme instance
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

// Create a client
const queryClient = new QueryClient();

// For demo purposes, we'll use a hardcoded user ID
const DEMO_USER_ID = 'user123';

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Container maxWidth="lg" sx={{ py: 4 }}>
          <Box sx={{ mb: 4 }}>
            <h1>Interview Insight</h1>
            <p>Upload, query, and manage your interview transcripts</p>
          </Box>
          
          <Box sx={{ 
            display: 'flex', 
            flexDirection: { xs: 'column', md: 'row' },
            gap: 3
          }}>
            {/* Main content area */}
            <Box sx={{ 
              flex: { md: '2' },
              display: 'flex',
              flexDirection: 'column',
              gap: 3
            }}>
              <Box>
                <TranscriptUpload userId={DEMO_USER_ID} />
              </Box>
              <Box>
                <TranscriptQuery userId={DEMO_USER_ID} />
              </Box>
            </Box>

            {/* Sidebar */}
            <Box sx={{ 
              flex: { md: '1' },
              minWidth: { md: '300px' }
            }}>
              <TranscriptList userId={DEMO_USER_ID} />
            </Box>
          </Box>
        </Container>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
