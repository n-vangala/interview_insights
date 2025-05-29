import React, { useState } from 'react';
import { Box, TextField, Button, Typography, Paper, CircularProgress, Alert } from '@mui/material';
import { useMutation } from '@tanstack/react-query';
import axios from 'axios';

interface TranscriptQueryProps {
  userId: string;
}

interface QueryResponse {
  answer: string;
  confidence: number;
}

const TranscriptQuery: React.FC<TranscriptQueryProps> = ({ userId }) => {
  const [query, setQuery] = useState('');
  const [error, setError] = useState<string | null>(null);

  const queryMutation = useMutation({
    mutationFn: async (question: string) => {
      const response = await axios.post<QueryResponse>('http://localhost:5000/query', {
        user_id: userId,
        question,
      });
      return response.data;
    },
    onError: (error) => {
      setError('Failed to get answer. Please try again.');
      console.error('Query error:', error);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      queryMutation.mutate(query.trim());
    }
  };

  return (
    <Box sx={{ p: 3, border: '1px solid #ddd', borderRadius: 1 }}>
      <Typography variant="h6" gutterBottom>
        Ask Questions
      </Typography>

      <form onSubmit={handleSubmit}>
        <TextField
          fullWidth
          multiline
          rows={3}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question about your interview..."
          variant="outlined"
          disabled={queryMutation.isPending}
          sx={{ mb: 2 }}
        />

        <Button
          type="submit"
          variant="contained"
          color="primary"
          disabled={!query.trim() || queryMutation.isPending}
        >
          {queryMutation.isPending ? (
            <>
              <CircularProgress size={24} sx={{ mr: 1 }} />
              Getting Answer...
            </>
          ) : (
            'Get Answer'
          )}
        </Button>
      </form>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {queryMutation.isSuccess && (
        <Paper sx={{ mt: 3, p: 2, bgcolor: 'background.default' }}>
          <Typography variant="subtitle1" gutterBottom>
            Answer:
          </Typography>
          <Typography variant="body1" paragraph>
            {queryMutation.data.answer}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Confidence: {(queryMutation.data.confidence * 100).toFixed(1)}%
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default TranscriptQuery; 